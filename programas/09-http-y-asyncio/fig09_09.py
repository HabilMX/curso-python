# fig09_09.py
import asyncio

import httpx


async def main() -> None:
    async with httpx.AsyncClient() as cliente:
        respuesta = await cliente.get("http://127.0.0.1:8099/pagos")
        print(respuesta.status_code)


asyncio.run(main())
