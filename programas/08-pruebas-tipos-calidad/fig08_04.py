# fig08_04.py
UMBRAL_LENTO_MS = 1000


def clasificar(codigo: int | None, tiempo_ms: int | None) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= UMBRAL_LENTO_MS:
        return "LENTO"
    return "ARRIBA"


def test_999_ms_es_arriba() -> None:
    assert clasificar(200, 999) == "ARRIBA"


def test_1000_ms_es_lento() -> None:
    assert clasificar(200, 1000) == "LENTO"


def test_un_503_es_caido() -> None:
    assert clasificar(503, 95) == "CAIDO"


def prueba_sin_respuesta_es_caido() -> None:
    assert clasificar(None, None) == "ARRIBA"
