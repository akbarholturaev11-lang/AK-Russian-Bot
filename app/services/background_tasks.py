import asyncio


def run_background(coro, label: str = "background_task"):
    async def _runner():
        try:
            await coro
        except Exception as e:
            print(f"{label} error:", e)

    asyncio.create_task(_runner())
