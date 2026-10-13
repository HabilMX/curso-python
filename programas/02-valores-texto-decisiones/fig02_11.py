# fig02_11.py
UMBRAL_LENTO_MS = 1000
codigo = None
tiempo_ms = None

if tiempo_ms >= UMBRAL_LENTO_MS:
    estado = "LENTO"
elif codigo is None or codigo >= 400:
    estado = "CAIDO"
else:
    estado = "ARRIBA"

print(estado)
