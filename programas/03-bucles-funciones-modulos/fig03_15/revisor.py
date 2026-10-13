# fig03_15/revisor.py
from formato import encabezado, linea

UMBRAL_LENTO_MS = 1000
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
CODIGOS = [200, 200, 200, None]
TIEMPOS_MS = [142, 2300, 87, None]


def clasificar(
    codigo: int | None, tiempo_ms: int | None, umbral_ms: int = UMBRAL_LENTO_MS
) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= umbral_ms:
        return "LENTO"
    return "ARRIBA"


def revisar(nombre: str, codigo: int | None, tiempo_ms: int | None) -> str:
    estado = clasificar(codigo, tiempo_ms)
    if codigo is None:
        detalle = "sin conexión"
    else:
        detalle = str(codigo)
    return linea(nombre, estado, tiempo_ms, detalle)


def main() -> None:
    print(encabezado())
    for i in range(len(NOMBRES)):
        print(revisar(NOMBRES[i], CODIGOS[i], TIEMPOS_MS[i]))


if __name__ == "__main__":
    main()
