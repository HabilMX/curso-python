# fig06_11.py
import tomllib

TEXTO = """
[[servicios]]
nombre = "catalogo"
url = "https://catalogo.example"

[[servicios]]
nombre = "notificaciones"
url = "https://notificaciones.example"
timeout_ms = 1000
"""

datos = tomllib.loads(TEXTO)
print(datos)

segundo = datos["servicios"][1]
print(segundo["nombre"], segundo["timeout_ms"], type(segundo["timeout_ms"]))
print(segundo.get("proxy"))
