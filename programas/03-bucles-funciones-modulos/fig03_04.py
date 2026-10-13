# fig03_04.py
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]

for i, nombre in enumerate(NOMBRES):
    print(i, nombre)

for numero, nombre in enumerate(NOMBRES, start=1):
    print(f"{numero}. {nombre}")
