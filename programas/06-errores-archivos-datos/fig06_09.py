# fig06_09.py
texto = "sin conexión"

en_utf8 = texto.encode("utf-8")
en_latin1 = texto.encode("latin-1")

print(en_utf8)
print(en_latin1)
print(len(texto), len(en_utf8), len(en_latin1))
print(en_utf8.decode("utf-8"))
