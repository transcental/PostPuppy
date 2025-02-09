import asyncio
import contextlib
import logging

import uvicorn
import uvloop
from dotenv import load_dotenv
from starlette.applications import Starlette

from postpuppy.utils.checker import run_shipment_checker
from postpuppy.utils.env import env
from postpuppy.utils.logging import send_heartbeat

load_dotenv()

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logging.basicConfig(level="INFO")


@contextlib.asynccontextmanager
async def main(_app: Starlette):
    await env.db.connect()
    asyncio.create_task(run_shipment_checker())
    await send_heartbeat(":neodog_verified: Post Puppy is online!")
    try:
        yield
    finally:
        await env.db.disconnect()


def start():
    uvicorn.run(
        "postpuppy.utils.starlette:app",
        host="0.0.0.0",
        port=env.port,
        log_level="info" if env.environment != "production" else "warning",
    )


if __name__ == "__main__":
    start()
