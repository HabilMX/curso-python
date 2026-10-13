# fig06_18/revisor.py
from pathlib import Path

from configuracion import ErrorDeConfiguracion, leer_servicios
from formato import encabezado, linea, resumen
from revision import revisar_todos

RUTA_CONFIG = Path("servicios.toml")


def main() -> None:
    try:
        servicios = leer_servicios(RUTA_CONFIG)
    except ErrorDeConfiguracion as error:
        print(f"error de configuración: {error}")
        return

    resultados = revisar_todos(servicios)
    print(encabezado())
    for resultado in resultados:
        print(linea(resultado))
    print()
    print(resumen(resultados))


if __name__ == "__main__":
    main()
