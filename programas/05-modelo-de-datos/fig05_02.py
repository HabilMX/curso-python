# fig05_02.py
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Servicio:
    nombre: str
    url: str
    timeout_ms: int = 5000


catalogo = Servicio("catalogo", "https://catalogo.example")
catalogo_corto = replace(catalogo, timeout_ms=1000)
print(catalogo.timeout_ms, catalogo_corto.timeout_ms)

repetido = Servicio("catalogo", "https://catalogo.example")
print(len({catalogo, repetido}))
