# fig06_02.py
def leer_tiempo(texto: str) -> int | None:
    try:
        tiempo_ms = int(texto)
    except ValueError:
        print(f"  '{texto}' no es un número entero")
        return None
    else:
        print(f"  '{texto}' se convirtió en {tiempo_ms}")
        return tiempo_ms
    finally:
        print("  (fin de la conversión)")


def main() -> None:
    for texto in ["142", "142 ms"]:
        print(f"leyendo '{texto}'")
        tiempo_ms = leer_tiempo(texto)
        print(f"  resultado: {tiempo_ms}")


if __name__ == "__main__":
    main()
