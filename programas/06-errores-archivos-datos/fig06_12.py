# fig06_12.py
import tomllib

TEXTO = """
[[servicios]]
nombre = "catalogo
url = "https://catalogo.example"
"""

try:
    tomllib.loads(TEXTO)
except tomllib.TOMLDecodeError as error:
    print(f"TOML inválido: {error}")
