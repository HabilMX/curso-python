# fig05_01.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Servicio:
    nombre: str
    url: str
    timeout_ms: int = 5000


catalogo = Servicio("catalogo", "https://catalogo.example")
notificaciones = Servicio(
    nombre="notificaciones",
    url="https://notificaciones.example",
    timeout_ms=1000,
)
print(catalogo)
print(notificaciones.timeout_ms)
print(catalogo.nombre, catalogo.timeout_ms)

igual = Servicio("catalogo", "https://catalogo.example")
print(catalogo == igual, catalogo is igual)

raro = Servicio(nombre=5, url=None)
print(raro)
