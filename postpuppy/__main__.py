import asyncio
import contextlib
import logging

import uvicorn
import uvloop
from dotenv import load_dotenv
from starlette.applications import Starlette

from postpuppy.utils.checker import check_for_shipment_updates
from postpuppy.utils.env import env

load_dotenv()

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logging.basicConfig(level="INFO")


@contextlib.asynccontextmanager
async def main(_app: Starlette):
    await env.async_init()
    await env.db.connect()
    asyncio.create_task(check_for_shipment_updates())
    try:
        yield
    finally:
        await env.db.disconnect()
        await env.async_close()


def start():
    uvicorn.run(
        "postpuppy.utils.starlette:app",
        host="0.0.0.0",
        port=env.port,
        log_level="info" if env.environment != "production" else "warning",
    )


if __name__ == "__main__":
    start()
