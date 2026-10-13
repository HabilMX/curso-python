# fig03_11.py
UMBRAL_LENTO_MS = 1000
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
CODIGOS = [200, 200, 200, None]
TIEMPOS_MS = [142, 2300, 87, None]


def formatear_tiempo(tiempo_ms: int | None) -> str:
    if tiempo_ms is None:
        return "—"
    if tiempo_ms < 1000:
        return f"{tiempo_ms}ms"
    return f"{tiempo_ms / 1000:.1f}s"


def encabezado() -> str:
    return f"{'SERVICIO':<12}{'ESTADO':<10}{'TIEMPO':>6}  {'DETALLE'}"


def linea(nombre: str, estado: str, tiempo_ms: int | None, detalle: str) -> str:
    tiempo = formatear_tiempo(tiempo_ms)
    return f"{nombre:<12}{estado:<10}{tiempo:>6}  {detalle}"


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


main()
