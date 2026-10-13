# fig04_08.py
tiempos_ms = [142, 2300, 87]

lentos: list[int] = []
for tiempo_ms in tiempos_ms:
    if tiempo_ms >= 1000:
        lentos.append(tiempo_ms)
print(lentos)

lentos = [tiempo_ms for tiempo_ms in tiempos_ms if tiempo_ms >= 1000]
print(lentos)

textos = [f"{tiempo_ms}ms" for tiempo_ms in tiempos_ms]
print(textos)
print(", ".join(textos))

por_servicio = {"catalogo": 142, "inventario": 2300, "pagos": 87, "reportes": None}
respondieron = {nombre: ms for nombre, ms in por_servicio.items() if ms is not None}
print(respondieron)
sin_respuesta = {nombre for nombre, ms in por_servicio.items() if ms is None}
print(sin_respuesta)
promedio_ms = round(sum(respondieron.values()) / len(respondieron))
print(promedio_ms)
