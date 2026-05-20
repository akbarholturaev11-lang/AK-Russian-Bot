import asyncio

from scripts.hsk4_lower_seed_data import run_upsert


upsert_lesson = run_upsert(20)


if __name__ == "__main__":
    asyncio.run(upsert_lesson())
