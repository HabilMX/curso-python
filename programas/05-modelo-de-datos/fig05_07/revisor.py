# fig05_07/revisor.py
from formato import encabezado, linea, resumen
from modelo import Servicio
from revision import revisar_todos

SERVICIOS: list[Servicio] = [
    Servicio("catalogo", "https://catalogo.example"),
    Servicio("inventario", "https://inventario.example"),
    Servicio("pagos", "https://pagos.example"),
    Servicio("reportes", "https://reportes.example"),
]


def main() -> None:
    resultados = revisar_todos(SERVICIOS)
    print(encabezado())
    for resultado in resultados:
        print(linea(resultado))
    print()
    print(resumen(resultados))


if __name__ == "__main__":
    main()
