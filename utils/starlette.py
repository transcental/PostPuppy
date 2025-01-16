from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route

from main import main
from utils.env import env
from utils.slack import app as slack_app

req_handler = AsyncSlackRequestHandler(slack_app)


async def endpoint(req: Request):
    return await req_handler.handle(req)


app = Starlette(
    debug=True if env.environment != "production" else False,
    routes=[
        Route(path="/slack/events", endpoint=endpoint, methods=["POST"])
    ],
    lifespan=main
)