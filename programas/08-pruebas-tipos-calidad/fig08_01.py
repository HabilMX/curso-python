# fig08_01.py
def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


def test_menos_de_un_segundo_va_en_milisegundos() -> None:
    assert formatear_tiempo(87) == "87ms"


def test_sin_tiempo_va_una_raya() -> None:
    assert formatear_tiempo(None) == "—"
