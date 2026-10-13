# fig10_04.py
import asyncio
import time


async def servicio_colgado() -> None:
    await asyncio.sleep(10)


async def main() -> None:
    inicio = time.perf_counter()
    try:
        async with asyncio.timeout(1):
            await servicio_colgado()
    except TimeoutError:
        print(f"tiempo agotado tras {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
