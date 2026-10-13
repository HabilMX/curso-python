# fig03_10.py
UMBRAL_LENTO_MS = 1000


def clasificar(
    codigo: int | None, tiempo_ms: int | None, umbral_ms: int = UMBRAL_LENTO_MS
) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= umbral_ms:
        return "LENTO"
    return "ARRIBA"


print(clasificar(200, 142))
print(clasificar(200, 999))
print(clasificar(200, 1000))
print(clasificar(200, 2300))
print(clasificar(503, 95))
print(clasificar(None, None))
print(clasificar(200, 142, umbral_ms=100))
print(clasificar(codigo=200, tiempo_ms=2300))
