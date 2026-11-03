"""Extrae precios de competidores a Excel con historial. Uso: python extractor.py config.yaml"""
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import yaml
from bs4 import BeautifulSoup

DB = "historial.db"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


def cargar_html(origen):
    if origen.startswith("http"):
        r = requests.get(origen, headers={"User-Agent": UA}, timeout=20)
        r.raise_for_status()
        return r.text
    return Path(origen).read_text(encoding="utf-8")


def precio_a_float(texto):
    return float(texto.replace("$", "").replace(",", "").strip())


def extraer(tienda):
    sopa = BeautifulSoup(cargar_html(tienda["url"]), "html.parser")
    filas = []
    for tarjeta in sopa.select(tienda["contenedor"]):
        nombre = tarjeta.select_one(tienda["nombre"])
        precio = tarjeta.select_one(tienda["precio"])
        if nombre is None or precio is None:
            continue
        try:
            filas.append((nombre.get_text(strip=True), precio_a_float(precio.get_text())))
        except ValueError:
            continue
    return filas


def main():
    if len(sys.argv) != 2:
        print("Uso: python extractor.py config.yaml")
        return 1

    cfg = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
    con = sqlite3.connect(DB)
    con.execute(
        """CREATE TABLE IF NOT EXISTS precios(
            id INTEGER PRIMARY KEY AUTOINCREMENT, tienda TEXT, producto TEXT,
            precio REAL, capturado TEXT)"""
    )

    ahora = datetime.now().isoformat(timespec="seconds")
    total = 0
    errores = 0

    for tienda in cfg["tiendas"]:
        try:
            filas = extraer(tienda)
        except Exception as e:
            errores += 1
            print(f"[!] {tienda['tienda']}: {e}")
            continue
        con.executemany(
            "INSERT INTO precios(tienda, producto, precio, capturado) VALUES(?,?,?,?)",
            [(tienda["tienda"], p, pr, ahora) for p, pr in filas],
        )
        total += len(filas)
        print(f"{tienda['tienda']}: {len(filas)} productos")

    if total == 0:
        print("Error: no se extrajo ningun producto")
        return 1

    con.commit()
    hoy = pd.read_sql(
        "SELECT tienda, producto, precio FROM precios WHERE capturado = ?",
        con, params=(ahora,),
    )
    historial = pd.read_sql(
        "SELECT tienda, producto, precio, capturado FROM precios ORDER BY capturado DESC LIMIT 500",
        con,
    )
    con.close()

    with pd.ExcelWriter("precios_hoy.xlsx", engine="openpyxl") as w:
        hoy.to_excel(w, sheet_name="Hoy", index=False)
        historial.to_excel(w, sheet_name="Historial", index=False)

    print(f"Total: {total} precios -> precios_hoy.xlsx")
    if errores:
        print(f"Tiendas con error: {errores}")
    return 0


if __name__ == "__main__":
    sys.exit(main())