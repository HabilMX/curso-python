# fig04_07.py
def nombres_repetidos(nombres: list[str]) -> set[str]:
    vistos: set[str] = set()
    repetidos: set[str] = set()
    for nombre in nombres:
        if nombre in vistos:
            repetidos.add(nombre)
        vistos.add(nombre)
    return repetidos


print(sorted(nombres_repetidos(["catalogo", "pagos", "catalogo", "reportes", "pagos"])))
print(sorted(nombres_repetidos(["catalogo", "inventario", "pagos", "reportes"])))
