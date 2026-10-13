# fig06_16.py
from urllib.parse import urlsplit

DIRECCIONES = [
    "https://catalogo.example",
    "http://127.0.0.1:8099/catalogo",
    "ftp://archivos.example",
    "file:///etc/hosts",
    "catalogo.example",
    "javascript:alert(1)",
]

for direccion in DIRECCIONES:
    esquema = urlsplit(direccion).scheme
    permitida = esquema in {"http", "https"}
    print(f"{direccion:<32} esquema='{esquema}' permitida={permitida}")
