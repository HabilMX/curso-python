# fig03_07.py
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
TIEMPOS_MS = [142, 2300, 87, None]

for i in range(len(NOMBRES)):
    if TIEMPOS_MS[i] is None:
        continue
    if TIEMPOS_MS[i] >= 1000:
        print("primer servicio lento:", NOMBRES[i])
        break
