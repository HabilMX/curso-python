# fig06_13.py
import json

resultado = {
    "nombre": "reportes",
    "estado": "CAIDO",
    "tiempo_ms": None,
    "detalle": "sin conexión",
    "activo": True,
}

texto = json.dumps(resultado, ensure_ascii=False, indent=2)
print(texto)

de_vuelta = json.loads(texto)
print(de_vuelta["tiempo_ms"] is None, de_vuelta == resultado)

print(json.dumps(resultado["detalle"]))
print(json.dumps(resultado["detalle"], ensure_ascii=False))
