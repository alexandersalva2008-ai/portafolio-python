# 02-resumen-cfdi

## Problema

Revisar a mano cientos de CFDI para saber cuanto se facturo a cada cliente y en que mes es lento y propenso a errores. Este script recorre una carpeta, lee los XML y arma un resumen en Excel agrupado por cliente y por mes, con una hoja de detalle.

Corre 100% local: los XML no se suben a ningun servicio. Funciona con CFDI 3.3 y 4.0 porque solo lee atributos del comprobante, emisor, receptor e impuestos, sin depender del nombre del namespace.

## Uso

```bash
pip install -r requirements.txt
python resumen_cfdi.py <carpeta>
```

El script busca archivos `*.xml` de forma recursiva dentro de la carpeta indicada. Los XML malformados se saltan y se cuentan al final. El resultado se escribe en `resumen.xlsx`, en el directorio actual, con las hojas `Por cliente`, `Por mes` y `Detalle`.

Ejemplo con los datos de prueba:

```bash
python resumen_cfdi.py ejemplos
```

Si la carpeta no existe o no tiene XML, el script termina con codigo 1 y un mensaje de error.

## Ejemplo de salida

```text
XML procesados: 3
Archivos saltados: 0
Resumen generado en: C:\ruta\al trabajo\resumen.xlsx
```

Hoja `Por cliente`:

| receptor_rfc | receptor_nombre | facturas | subtotal | iva | total |
| --- | --- | --- | --- | --- | --- |
| XYZ010101XY1 | CLIENTE UNO SA DE CV | 2 | 15000.0 | 2400.0 | 17400.0 |
| QRS010101QR1 | CLIENTE DOS SA DE CV | 1 | 8000.0 | 1280.0 | 9280.0 |

Los montos del ejemplo usan datos inventados.
