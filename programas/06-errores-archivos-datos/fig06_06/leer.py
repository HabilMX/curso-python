# fig06_06/leer.py
with open("nota.txt", encoding="utf-8") as archivo:
    texto = archivo.read()
    print(f"dentro del with: cerrado = {archivo.closed}")

print(f"fuera del with: cerrado = {archivo.closed}")
print(texto.splitlines())
