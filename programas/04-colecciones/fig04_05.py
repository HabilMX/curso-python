# fig04_05.py
tiempos_ms = {"catalogo": 142, "inventario": 2300, "pagos": 87, "reportes": None}
print(tiempos_ms["pagos"])
print(len(tiempos_ms))
print("pagos" in tiempos_ms, "gateway" in tiempos_ms)

print(tiempos_ms.get("gateway"))
print(tiempos_ms.get("gateway", "sin dato"))
print(tiempos_ms.get("reportes"))
print("reportes" in tiempos_ms, tiempos_ms.get("reportes"), tiempos_ms.get("gateway"))

tiempos_ms["facturacion"] = 95
for nombre, ms in tiempos_ms.items():
    print(nombre, ms)

print(list(tiempos_ms))
print(list(tiempos_ms.values()))
