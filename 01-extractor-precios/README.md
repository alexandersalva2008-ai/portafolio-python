# Extractor de precios a Excel con historial

## Problema
Una comercializadora revisa a mano los precios de sus competidores cada mañana.
Este script los extrae, los guarda con fecha en una base local y entrega un Excel.

## Uso
1. Instala dependencias: pip install -r requirements.txt
2. Ajusta los selectores en config.yaml (una entrada por tienda).
3. Corre: python extractor.py config.yaml
4. Se genera precios_hoy.xlsx con las hojas Hoy e Historial.

## Ejemplo de salida
    tienda_a: 4 productos
    tienda_b: 4 productos
    Total: 8 precios -> precios_hoy.xlsx

## Notas
- La hoja Historial conserva las ultimas 500 capturas con fecha.
- Si una tienda falla, se reporta y el proceso continua con las demas.
- Para sitios con JavaScript hay una variante con Selenium.