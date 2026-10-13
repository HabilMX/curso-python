# fig09_10.py
import asyncio
import time


async def esperar(nombre: str, segundos: float) -> str:
    await asyncio.sleep(segundos)
    return f"{nombre} esperó {segundos} s"


async def main() -> None:
    inicio = time.perf_counter()
    for nombre in ("catalogo", "inventario", "pagos"):
        print(await esperar(nombre, 0.5))
    total = time.perf_counter() - inicio
    print(f"en serie tarda la suma, 1.5 s o más: {1.5 <= total < 2.0}")


asyncio.run(main())
