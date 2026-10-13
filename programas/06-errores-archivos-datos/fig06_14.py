# fig06_14.py
import json

TEXTO = """{
  "nombre": "pagos",
  "tiempo_ms": 87
  "estado": "ARRIBA"
}"""

try:
    json.loads(TEXTO)
except json.JSONDecodeError as error:
    print(f"mensaje: {error.msg}")
    print(f"línea {error.lineno}, columna {error.colno}")
    print(f"completo: {error}")
