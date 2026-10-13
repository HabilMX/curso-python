# fig03_06.py
TIEMPOS_MS = [142, 2300, 87, None]

total = 0
respondieron = 0
for tiempo_ms in TIEMPOS_MS:
    if tiempo_ms is not None:
        total += tiempo_ms
        respondieron += 1

print("suma:", total, "ms")
print("respondieron:", respondieron)
print("promedio:", total / respondieron, "ms")
