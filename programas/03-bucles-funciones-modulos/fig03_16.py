# fig03_16.py
def registrar_caido(nombre: str, caidos: list[str] | None = None) -> list[str]:
    if caidos is None:
        caidos = []
    caidos.append(nombre)
    return caidos


print(registrar_caido("reportes"))
print(registrar_caido("facturacion"))
historial = []
registrar_caido("reportes", historial)
registrar_caido("facturacion", historial)
print(historial)
