# fig06_01.py
def leer_tiempo(texto: str) -> int:
    return int(texto)


def main() -> None:
    tiempo_ms = leer_tiempo("142 ms")
    print(f"tiempo: {tiempo_ms}")


if __name__ == "__main__":
    main()
