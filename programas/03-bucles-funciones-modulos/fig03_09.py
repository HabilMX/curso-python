# fig03_09.py
def decir_tiempo(tiempo_ms: int) -> None:
    print(f"{tiempo_ms}ms")


def dar_tiempo(tiempo_ms: int) -> str:
    return f"{tiempo_ms}ms"


a = decir_tiempo(87)
b = dar_tiempo(87)
print(a)
print(b)
print(type(a))
print(type(b))
