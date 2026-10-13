# fig04_03.py
resultado = (200, 142, None)
print(resultado[0], resultado[1])
codigo, tiempo_ms, error = resultado
print(f"código {codigo}, tiempo {tiempo_ms}, error {error}")
print(len(resultado))

pares = [("catalogo", 142), ("pagos", 87)]
for nombre, ms in pares:
    print(f"{nombre} respondió en {ms}ms")

uno = (200,)
no_es_tupla = 200
print(type(uno), type(no_es_tupla))
