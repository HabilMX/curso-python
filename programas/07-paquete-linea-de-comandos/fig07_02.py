# fig07_02.py
import argparse

parser = argparse.ArgumentParser(description="Demostración de argparse.")
parser.add_argument("--config", default="servicios.toml")
parser.add_argument("--formato", choices=["tabla", "json"], default="tabla")

argumentos = parser.parse_args()
print(f"config = {argumentos.config}")
print(f"formato = {argumentos.formato}")
