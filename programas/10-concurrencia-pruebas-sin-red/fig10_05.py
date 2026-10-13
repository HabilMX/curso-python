# fig10_05.py
import asyncio
import time


async def consultar(semaforo: asyncio.Semaphore, numero: int) -> None:
    async with semaforo:
        print(f"servicio {numero}: entra")
        await asyncio.sleep(0.5)
        print(f"servicio {numero}: sale")


async def main() -> None:
    semaforo = asyncio.Semaphore(2)
    inicio = time.perf_counter()
    async with asyncio.TaskGroup() as grupo:
        for numero in range(1, 7):
            grupo.create_task(consultar(semaforo, numero))
    print(f"seis servicios, de dos en dos: {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
