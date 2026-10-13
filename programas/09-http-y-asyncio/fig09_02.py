# fig09_02.py
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

DIRECCIONES = {
    "catalogo": "http://127.0.0.1:8099/catalogo",
    "facturacion": "http://127.0.0.1:8099/facturacion",
    "reportes": "http://127.0.0.1:8098/",
}

for nombre, direccion in DIRECCIONES.items():
    try:
        with urlopen(direccion) as respuesta:
            print(nombre, "respondió", respuesta.status)
    except HTTPError as error:
        print(nombre, "respondió con un error", error.code)
    except URLError as error:
        print(nombre, "no se pudo conectar:", type(error.reason).__name__)
