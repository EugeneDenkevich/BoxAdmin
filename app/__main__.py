import asyncio

from app.entrypoint import entrypoint


async def main() -> None:
    await entrypoint()


if __name__ == "__main__":
    asyncio.run(main())
