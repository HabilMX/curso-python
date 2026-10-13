# fig03_08.py
def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


print(formatear_tiempo(87))
print(formatear_tiempo(999))
print(formatear_tiempo(1000))
print(formatear_tiempo(2300))
print(formatear_tiempo(None))
