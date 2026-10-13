# fig03_12.py
UMBRAL_LENTO_MS = 1000


def es_lento(tiempo_ms: int) -> bool:
    limite = UMBRAL_LENTO_MS
    return tiempo_ms >= limite


print(es_lento(2300))
print(es_lento(142))
