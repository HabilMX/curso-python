# fig08_11.py
def segundos(tiempo_ms: int | None) -> float | None:
    if tiempo_ms is None:
        return None
    return tiempo_ms / 1000


print(segundos(87))
try:
    print(segundos(None))
except TypeError as error:
    print(f"se rompió: {error}")
