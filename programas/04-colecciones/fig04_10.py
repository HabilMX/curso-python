# fig04_10.py
def agregar_reportes(nombres: list[str]) -> None:
    nombres.append("reportes")


base = ["catalogo", "pagos"]
agregar_reportes(base)
print(base)
