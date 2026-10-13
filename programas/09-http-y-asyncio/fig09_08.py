# fig09_08.py
import asyncio


async def saludar() -> str:
    return "hola"


print(asyncio.run(saludar()))
