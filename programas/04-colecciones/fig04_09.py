# fig04_09.py
principales = ["catalogo", "pagos"]
respaldo = principales
respaldo.append("reportes")
print(principales)
print(principales is respaldo)

copia = principales.copy()
copia.append("inventario")
print(principales)
print(copia)
print(principales is copia)

a = 5
b = a
b = b + 1
print(a, b)
