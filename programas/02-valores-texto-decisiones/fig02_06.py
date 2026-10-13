# fig02_06.py
UMBRAL_LENTO_MS = 1000
codigo = 200
tiempo_ms = 2300

if codigo is None or codigo >= 400:
    estado = "CAIDO"
elif tiempo_ms >= UMBRAL_LENTO_MS:
    estado = "LENTO"
else:
    estado = "ARRIBA"

print(estado)
