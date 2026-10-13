# fig06_18/ver_json.py
from configuracion import leer_servicios
from formato import reporte_a_json
from revision import revisar_todos
from revisor import RUTA_CONFIG

servicios = leer_servicios(RUTA_CONFIG)
print(reporte_a_json(revisar_todos(servicios)))
