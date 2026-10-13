# fig06_07/ruta.py
from pathlib import Path

ruta = Path("nota.txt")
print(ruta.name, ruta.suffix, ruta.exists())
print(Path("no-esta.txt").exists())

otra = Path("datos") / "servicios.toml"
print(otra)

texto = ruta.read_text(encoding="utf-8")
print(texto.splitlines())
