# fig03_03.py
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
TIEMPOS_MS = [142, 2300, 87, None]

for i in range(3):
    print(i)

for i in range(len(NOMBRES)):
    print(i, NOMBRES[i], TIEMPOS_MS[i])
