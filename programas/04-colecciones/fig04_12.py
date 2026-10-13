# fig04_12.py
tiempos_ms = [142, 2300, 87, 95]
for tiempo_ms in tiempos_ms:
    if tiempo_ms < 100:
        tiempos_ms.remove(tiempo_ms)
print(tiempos_ms)
