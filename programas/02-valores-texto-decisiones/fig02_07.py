# fig02_07.py
UMBRAL_LENTO_MS = 1000

nombre = "inventario"
url = "https://inventario.example"  # todavía no se usa: la ocupará la lección 9
codigo = 200
tiempo_ms = 2300

if codigo is None or codigo >= 400:
    estado = "CAIDO"
elif tiempo_ms >= UMBRAL_LENTO_MS:
    estado = "LENTO"
else:
    estado = "ARRIBA"

if tiempo_ms is None:
    tiempo = "—"
elif tiempo_ms < 1000:  # 1000 ms es un segundo, no el umbral de lento
    tiempo = f"{tiempo_ms}ms"
else:
    tiempo = f"{tiempo_ms / 1000:.1f}s"

if codigo is None:
    detalle = "sin conexión"
else:
    detalle = str(codigo)

print(f"{'SERVICIO':<12}{'ESTADO':<10}{'TIEMPO':>6}  {'DETALLE'}")
print(f"{nombre:<12}{estado:<10}{tiempo:>6}  {detalle}")
