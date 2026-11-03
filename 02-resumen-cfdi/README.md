# 02-resumen-cfdi


## Problema
Un despacho contable con 40 clientes recibe cientos de XML al mes y los captura a mano.
Este script consolida los comprobantes de ingreso en un Excel: totales por cliente, por mes y detalle.

## Uso
1. Instala dependencias: pip install -r requirements.txt
2. Arrastra la carpeta del mes y corre:
   python resumen_cfdi.py ruta\a\la\carpeta
3. Se genera resumen.xlsx con las hojas Por cliente, Por mes y Detalle.

Corre 100% local: los datos no salen de tu computadora.

## Ejemplo de salida
    Comprobantes de ingreso procesados: 3
    Archivos saltados: 0 | ignorados por tipo: 0
    Resumen generado en: C:\...\resumen.xlsx

## Limitaciones
- Solo procesa comprobantes de tipo Ingreso (I). Notas de credito y traslados se ignoran y se reportan.
- Un XML malformado se salta sin detener el proceso.
