# fig10_01.py
import asyncio
import time

ESPERAS_S = {"catalogo": 0.3, "inventario": 0.5, "pagos": 0.1, "reportes": 0.2}


async def consultar(nombre: str, espera_s: float) -> str:
    await asyncio.sleep(espera_s)
    print(f"{nombre}: respondió")
    return nombre


async def main() -> None:
    inicio = time.perf_counter()
    for nombre, espera_s in ESPERAS_S.items():
        await consultar(nombre, espera_s)
    print(f"en serie: {time.perf_counter() - inicio:.1f} s")


asyncio.run(main())
