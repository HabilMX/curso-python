# fig06_15.py
print(isinstance(True, int))
print(isinstance(True, bool))
print(True + True)


def timeout_valido(valor: object) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


for valor in [5000, 0, -1, True, "5000", 2.5]:
    print(valor, type(valor), timeout_valido(valor))
