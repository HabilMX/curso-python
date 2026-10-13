# fig10_02.py
import asyncio
import time

ESPERAS_S = {"catalogo": 0.3, "inventario": 0.5, "pagos": 0.1, "reportes": 0.2}


async def consultar(nombre: str, espera_s: float) -> str:
    print(f"{nombre}: empieza")
    await asyncio.sleep(espera_s)
    print(f"{nombre}: respondió")
    return nombre


async def main() -> None:
    inicio = time.perf_counter()
    async with asyncio.TaskGroup() as grupo:
        tareas = [
            grupo.create_task(consultar(nombre, espera_s))
            for nombre, espera_s in ESPERAS_S.items()
        ]
    print(f"a la vez: {time.perf_counter() - inicio:.1f} s")
    print([tarea.result() for tarea in tareas])


asyncio.run(main())
