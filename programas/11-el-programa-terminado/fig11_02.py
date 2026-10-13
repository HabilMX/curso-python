# fig11_02.py
import subprocess

nombre = "catalogo; echo INYECTADO"

print("--- con shell=True y un texto armado ---", flush=True)
subprocess.run(f"echo revisando {nombre}", shell=True, check=True)

print("--- con una lista y sin shell ---", flush=True)
subprocess.run(["echo", "revisando", nombre], check=True)
