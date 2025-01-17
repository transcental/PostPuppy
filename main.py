import asyncio
import contextlib
import logging

import uvicorn
import uvloop
from dotenv import load_dotenv
from starlette.applications import Starlette

from utils.env import env

logging.basicConfig(
    level=logging.INFO,
)

load_dotenv()

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


@contextlib.asynccontextmanager
async def main(_app: Starlette):
    await env.async_init()
    await env.db.connect()
    try:
        yield
    finally:
        await env.db.disconnect()
        await env.async_close()


if __name__ == "__main__":
    uvicorn.run(
        "utils.starlette:app",
        host="0.0.0.0",
        port=env.port,
        log_level="info" if env.environment != "production" else "warning",
    )
