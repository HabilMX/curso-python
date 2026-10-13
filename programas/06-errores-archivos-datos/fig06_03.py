# fig06_03.py
def leer_tiempo(texto: str) -> int | None:
    try:
        return int(texto.stirp())
    except Exception:  # noqa: BLE001
        print(f"'{texto}' no es un número entero")
        return None


def main() -> None:
    print(leer_tiempo("142"))


if __name__ == "__main__":
    main()
