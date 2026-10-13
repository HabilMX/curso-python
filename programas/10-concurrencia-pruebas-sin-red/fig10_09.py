# fig10_09.py
import asyncio


async def promedio(tiempos_ms: list[int]) -> float:
    return sum(tiempos_ms) / len(tiempos_ms)


async def main() -> None:
    async with asyncio.TaskGroup() as grupo:
        grupo.create_task(promedio([142, 87]))
        grupo.create_task(promedio([]))


asyncio.run(main())
