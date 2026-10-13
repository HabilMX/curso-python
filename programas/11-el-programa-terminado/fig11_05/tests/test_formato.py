# fig11_05/tests/test_formato.py
import json

import pytest

from revisor.formato import formatear_tiempo, reporte_a_json, tabla
from revisor.modelo import Estado, Resultado, Servicio


@pytest.mark.parametrize(
    ("tiempo_ms", "esperado"),
    [(None, "—"), (87, "87ms"), (999, "999ms"), (2300, "2.3s")],
)
def test_formatear_tiempo(tiempo_ms: int | None, esperado: str) -> None:
    assert formatear_tiempo(tiempo_ms) == esperado


def servicio(nombre: str) -> Servicio:
    return Servicio(nombre, f"https://{nombre}.example")


CANONICOS = [
    Resultado(servicio("catalogo"), Estado.ARRIBA, 142, "200"),
    Resultado(servicio("inventario"), Estado.LENTO, 2300, "200"),
    Resultado(servicio("pagos"), Estado.ARRIBA, 87, "200"),
    Resultado(servicio("reportes"), Estado.CAIDO, None, "sin conexión"),
]


def test_el_json_es_un_contrato() -> None:
    esperado = {
        "servicios": [
            {
                "nombre": "catalogo",
                "url": "https://catalogo.example",
                "estado": "ARRIBA",
                "tiempo_ms": 142,
                "detalle": "200",
            },
            {
                "nombre": "inventario",
                "url": "https://inventario.example",
                "estado": "LENTO",
                "tiempo_ms": 2300,
                "detalle": "200",
            },
            {
                "nombre": "pagos",
                "url": "https://pagos.example",
                "estado": "ARRIBA",
                "tiempo_ms": 87,
                "detalle": "200",
            },
            {
                "nombre": "reportes",
                "url": "https://reportes.example",
                "estado": "CAIDO",
                "tiempo_ms": None,
                "detalle": "sin conexión",
            },
        ],
        "resumen": {
            "total": 4,
            "arriba": 2,
            "lento": 1,
            "caido": 1,
            "promedio_ms": 843,
        },
    }
    assert json.loads(reporte_a_json(CANONICOS)) == esperado


def test_la_tabla_se_alinea_con_un_nombre_largo() -> None:
    largo = Resultado(servicio("notificaciones-de-clientes"), Estado.ARRIBA, 50, "200")
    lineas = tabla([*CANONICOS, largo]).splitlines()
    ancho = len("notificaciones-de-clientes") + 2
    assert lineas[0].index("ESTADO") == ancho
    for renglon in lineas[1:6]:
        assert renglon[ancho : ancho + 6] in {"ARRIBA", "LENTO ", "CAIDO "}
