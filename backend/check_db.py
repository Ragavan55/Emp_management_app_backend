import asyncio
import traceback

from app.db import init_db

async def main():
    try:
        await init_db()
        print("DB init succeeded")
    except Exception as e:
        traceback.print_exc()
        print("DB init failed:", e)

if __name__ == '__main__':
    asyncio.run(main())
