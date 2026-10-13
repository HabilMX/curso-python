# fig04_06.py
registrados = ["catalogo", "pagos", "catalogo", "reportes", "pagos"]
unicos = set(registrados)
print(len(registrados), len(unicos))
print(sorted(unicos))

arriba = {"catalogo", "pagos"}
todos = {"catalogo", "inventario", "pagos", "reportes"}
print("pagos" in arriba)
print(sorted(todos - arriba))
print(sorted(todos & arriba))
print(sorted(arriba | {"gateway"}))
arriba.add("pagos")
arriba.add("inventario")
print(sorted(arriba))
print(type({}), type(set()))
