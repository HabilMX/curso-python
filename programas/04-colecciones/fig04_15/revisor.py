# fig04_15/revisor.py
from formato import encabezado, linea

UMBRAL_LENTO_MS = 1000
SERVICIOS = ["catalogo", "inventario", "pagos", "reportes"]
SIMULADO: dict[str, tuple[int | None, int | None, str | None]] = {
    "catalogo": (200, 142, None),
    "inventario": (200, 2300, None),
    "pagos": (200, 87, None),
    "reportes": (None, None, "sin conexión"),
}


def clasificar(
    codigo: int | None, tiempo_ms: int | None, umbral_ms: int = UMBRAL_LENTO_MS
) -> str:
    if codigo is None or codigo >= 400:
        return "CAIDO"
    if tiempo_ms is not None and tiempo_ms >= umbral_ms:
        return "LENTO"
    return "ARRIBA"


def revisar(nombre: str) -> str:
    sin_respuesta = (None, None, "sin conexión")
    codigo, tiempo_ms, error = SIMULADO.get(nombre, sin_respuesta)
    if codigo is not None:
        detalle = str(codigo)
    elif error is not None:
        detalle = error
    else:
        detalle = "sin conexión"
    estado = clasificar(codigo, tiempo_ms)
    return linea(nombre, estado, tiempo_ms, detalle)


def main() -> None:
    renglones = [revisar(nombre) for nombre in SERVICIOS]
    print(encabezado())
    for renglon in renglones:
        print(renglon)


if __name__ == "__main__":
    main()
