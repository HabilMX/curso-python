# fig02_02.py
UMBRAL_LENTO_MS = 1000
tiempo_ms = 2300
codigo = 200

# Aritmética
print(tiempo_ms / 1000)
print(tiempo_ms // 1000)
print(tiempo_ms % 1000)
print(tiempo_ms + 100)
print(2**3)

# Comparaciones
print(tiempo_ms >= UMBRAL_LENTO_MS)
print(codigo == 200)
print(codigo != 200)

# Lógicos
print(codigo >= 400 or tiempo_ms >= UMBRAL_LENTO_MS)
print(codigo == 200 and tiempo_ms < UMBRAL_LENTO_MS)
contesto_bien = codigo < 400
print(not contesto_bien)
