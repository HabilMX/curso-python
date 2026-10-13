# fig06_04.py
class ErrorDeConfiguracion(Exception):
    """La configuración no se puede usar."""


def leer_timeout_ms(texto: str) -> int:
    try:
        return int(texto)
    except ValueError as error:
        mensaje = f"'timeout_ms' debe ser un entero, llegó '{texto}'"
        raise ErrorDeConfiguracion(mensaje) from error


def main() -> None:
    try:
        timeout_ms = leer_timeout_ms("cinco mil")
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}")
        print(f"causa original: {error.__cause__}")
    else:
        print(f"timeout_ms = {timeout_ms}")


if __name__ == "__main__":
    main()
