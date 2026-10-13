# fig04_01.py
nombres = ["catalogo", "inventario", "pagos", "reportes"]
print(nombres[0], nombres[3])
print(nombres[-1], nombres[-2])
print(nombres[1:3])
print(len(nombres))
print("pagos" in nombres, "gateway" in nombres)

nombres.append("facturacion")
print(nombres)
ultimo = nombres.pop()
print(ultimo, len(nombres))

tiempos_ms = [142, 2300, 87]
print(sorted(tiempos_ms), tiempos_ms)
tiempos_ms.sort()
print(tiempos_ms)
print(sum(tiempos_ms), min(tiempos_ms), max(tiempos_ms))
