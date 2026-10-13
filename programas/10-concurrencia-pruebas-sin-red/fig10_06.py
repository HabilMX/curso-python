# fig10_06.py
import asyncio


async def consulta_buena(nombre: str, espera_s: float) -> None:
    try:
        await asyncio.sleep(espera_s)
        print(f"{nombre}: terminó")
    except asyncio.CancelledError:
        print(f"{nombre}: cancelada")
        raise


async def consulta_rota(nombre: str) -> None:
    await asyncio.sleep(0.1)
    raise ConnectionError(f"{nombre}: sin conexión")


async def main() -> None:
    try:
        async with asyncio.TaskGroup() as grupo:
            grupo.create_task(consulta_buena("catalogo", 0.05))
            grupo.create_task(consulta_rota("reportes"))
            grupo.create_task(consulta_buena("inventario", 0.5))
    except* ConnectionError as grupo_de_errores:
        for error in grupo_de_errores.exceptions:
            print(f"falló: {error}")
    print("fin")


asyncio.run(main())
