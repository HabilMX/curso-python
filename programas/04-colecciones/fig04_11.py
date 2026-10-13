# fig04_11.py
import copy

grupos = [["catalogo", "pagos"], ["reportes"]]
superficial = grupos.copy()
superficial[1].append("inventario")
print(grupos)
print(grupos[1] is superficial[1])

grupos = [["catalogo", "pagos"], ["reportes"]]
profunda = copy.deepcopy(grupos)
profunda[1].append("inventario")
print(grupos)
print(profunda)
