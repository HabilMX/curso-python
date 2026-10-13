# fig03_14/medidas.py
print("medidas.py: __name__ vale", __name__)


def segundos(tiempo_ms: int) -> float:
    return tiempo_ms / 1000


if __name__ == "__main__":
    print("medidas.py se está ejecutando directamente")
    print(segundos(2300))
