# fig09_01.py
import time
from urllib.request import urlopen

inicio = time.perf_counter()
with urlopen("http://127.0.0.1:8099/catalogo") as respuesta:
    print(respuesta.status, respuesta.reason)
    cuerpo = respuesta.read()
print(cuerpo)
print(cuerpo.decode("utf-8"))
tardo_ms = (time.perf_counter() - inicio) * 1000
print(f"tardó 142 ms o más: {tardo_ms >= 142}")
