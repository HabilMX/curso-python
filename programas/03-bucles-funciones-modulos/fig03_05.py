# fig03_05.py
NOMBRES = ["catalogo", "inventario", "pagos", "reportes"]
CODIGOS = [200, 200, 200, None]

i = 0
while i < len(CODIGOS) and CODIGOS[i] is not None:
    i += 1

print("primer servicio sin respuesta, en la posición", i)
print(NOMBRES[i])
