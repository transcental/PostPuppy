from datetime import datetime

from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler
from slack_sdk.errors import SlackApiError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from postpuppy.__main__ import main
from postpuppy.utils.env import env
from postpuppy.utils.langs import LANGUAGES
from postpuppy.utils.signing import get_viewer_signature
from postpuppy.utils.slack import app as slack_app

req_handler = AsyncSlackRequestHandler(slack_app)


async def endpoint(req: Request):
    return await req_handler.handle(req)


async def health(req: Request):
    res = {}
    try:
        async with env.aiohttp_session.get(
            "https://shipment-viewer.hackclub.com"
        ) as resp:
            if resp.status == 200:
                res["shipment_viewer_online"] = True
            else:
                res["shipment_viewer_online"] = False
    except Exception:
        res["shipment_viewer_online"] = False

    try:
        users = await env.db.user.count()
        if users:
            res["database_online"] = True
            res["total_users"] = users
    except Exception:
        res["database_online"] = False

    try:
        await env.slack_client.auth_test()
        res["slack_online"] = True
    except SlackApiError:
        res["slack_online"] = False

    if (
        res.get("shipment_viewer_online")
        and res.get("database_online")
        and res.get("slack_online")
    ):
        res["healthy"] = True
    else:
        res["healthy"] = False

    return JSONResponse(res)


async def verify(req: Request):
    user_id = req.query_params.get("user_id")
    email = req.query_params.get("email")
    signature = req.query_params.get("signature")
    if not user_id or not email or not signature:
        return PlainTextResponse("Invalid verification link", status_code=400)

    user = await env.db.user.find_first(where={"id": user_id})
    if not user:
        return PlainTextResponse("Invalid user", status_code=400)

    if not user.email or user.email != email:
        return PlainTextResponse("Invalid email", status_code=400)

    if not user.emailSignature or not user.emailSignatureExpiry:
        return PlainTextResponse(
            "Uh oh, something went wrong, please message amber on Slack",
            status_code=500,
        )

    if datetime.now().timestamp() > user.emailSignatureExpiry.timestamp():
        return PlainTextResponse("Link expired", status_code=400)

    if user.emailSignature != signature:
        return PlainTextResponse("Invalid signature", status_code=400)

    shipment_link = await get_viewer_signature(email)
    api_link = shipment_link.replace("shipments", "jason")

    await env.db.user.update(
        where={"id": user_id},
        data={"verifiedEmail": True, "viewerUrl": shipment_link, "apiUrl": api_link},
    )

    language = LANGUAGES.get(user.language, LANGUAGES["dog"])["utils.starlette"]

    await env.slack_client.chat_postMessage(
        channel=user_id,
        icon_emoji=language["icon_emoji"],
        username=language["display_name"],
        text=language["verified_slack"]["text"],
        blocks=language["verified_slack"]["blocks"],
    )

    return PlainTextResponse("Email verified", status_code=200)


app = Starlette(
    debug=True if env.environment != "production" else False,
    routes=[
        Route(path="/slack/events", endpoint=endpoint, methods=["POST"]),
        Route(path="/verify", endpoint=verify, methods=["GET"]),
        Route(path="/health", endpoint=health, methods=["GET"]),
    ],
    lifespan=main,
)
