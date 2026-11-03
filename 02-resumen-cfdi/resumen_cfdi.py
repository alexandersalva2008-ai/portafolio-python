import sys
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd


def etiqueta_local(elemento):
    return elemento.tag.split("}")[-1]


def buscar_hijo(padre, nombre):
    for hijo in padre:
        if etiqueta_local(hijo) == nombre:
            return hijo
    return None


def texto_atributo(elemento, atributo, defecto=""):
    if elemento is None:
        return defecto
    return elemento.get(atributo, defecto)


def numero_atributo(elemento, atributo, defecto=0.0):
    if elemento is None:
        return defecto
    valor = elemento.get(atributo)
    if valor is None or valor == "":
        return defecto
    try:
        return float(valor)
    except ValueError:
        return defecto


def extraer_comprobante(ruta):
    arbol = ET.parse(ruta)
    raiz = arbol.getroot()

    if etiqueta_local(raiz) != "Comprobante":
        raise ValueError("el archivo no es un CFDI")

    emisor = buscar_hijo(raiz, "Emisor")
    receptor = buscar_hijo(raiz, "Receptor")
    impuestos = buscar_hijo(raiz, "Impuestos")

    return {
        "archivo": ruta.name,
        "receptor_rfc": texto_atributo(receptor, "Rfc"),
        "receptor_nombre": texto_atributo(receptor, "Nombre"),
        "emisor_rfc": texto_atributo(emisor, "Rfc"),
        "emisor_nombre": texto_atributo(emisor, "Nombre"),
        "subtotal": numero_atributo(raiz, "SubTotal"),
        "iva": numero_atributo(impuestos, "TotalImpuestosTrasladados"),
        "total": numero_atributo(raiz, "Total"),
        "moneda": raiz.get("Moneda", "MXN"),
        "fecha": raiz.get("Fecha", ""),
        "tipo": raiz.get("TipoDeComprobante", ""),
    }


def main():
    if len(sys.argv) != 2:
        print("Uso: python resumen_cfdi.py <carpeta>")
        return 1

    carpeta = Path(sys.argv[1])
    if not carpeta.is_dir():
        print(f"Error: la carpeta no existe: {carpeta}")
        return 1

    archivos = sorted(carpeta.rglob("*.xml"))
    if not archivos:
        print(f"Error: no se encontraron archivos XML en {carpeta}")
        return 1

    registros = []
    saltados = 0
    ignorados = 0

    for ruta in archivos:
        try:
            registro = extraer_comprobante(ruta)
        except (ET.ParseError, OSError, ValueError):
            saltados += 1
            print(f"Advertencia: XML saltado por error: {ruta}")
            continue
        if registro["tipo"] != "I":
            ignorados += 1
            continue
        registros.append(registro)

    if not registros:
        print("Error: ningun comprobante de ingreso pudo procesarse")
        print(f"Archivos saltados: {saltados} | ignorados por tipo: {ignorados}")
        return 1

    detalle = pd.DataFrame(registros)
    detalle["mes"] = (
        pd.to_datetime(detalle["fecha"], errors="coerce")
        .dt.to_period("M")
        .astype(str)
    )

    por_cliente = (
        detalle.groupby(["receptor_rfc", "receptor_nombre"], as_index=False)
        .agg(
            facturas=("archivo", "count"),
            subtotal=("subtotal", "sum"),
            iva=("iva", "sum"),
            total=("total", "sum"),
        )
        .sort_values("total", ascending=False)
    )

    por_mes = (
        detalle.groupby("mes", as_index=False)
        .agg(
            facturas=("archivo", "count"),
            subtotal=("subtotal", "sum"),
            iva=("iva", "sum"),
            total=("total", "sum"),
        )
        .sort_values("mes")
    )

    detalle_salida = detalle[
        [
            "archivo",
            "fecha",
            "tipo",
            "emisor_rfc",
            "emisor_nombre",
            "receptor_rfc",
            "receptor_nombre",
            "moneda",
            "subtotal",
            "iva",
            "total",
        ]
    ]

    salida = Path("resumen.xlsx")
    with pd.ExcelWriter(salida, engine="openpyxl") as escritor:
        por_cliente.to_excel(escritor, sheet_name="Por cliente", index=False)
        por_mes.to_excel(escritor, sheet_name="Por mes", index=False)
        detalle_salida.to_excel(escritor, sheet_name="Detalle", index=False)

    print(f"Comprobantes de ingreso procesados: {len(registros)}")
    print(f"Archivos saltados: {saltados} | ignorados por tipo: {ignorados}")
    print(f"Resumen generado en: {salida.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())