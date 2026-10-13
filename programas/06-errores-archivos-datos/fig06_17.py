# fig06_17.py
# DEMOSTRACIÓN de lo que NO se hace: eval con un texto que viene de fuera.
print(eval("2300 + 1"))

texto_de_fuera = "print('esto lo escribió otro y se ejecutó')"
eval(texto_de_fuera)
