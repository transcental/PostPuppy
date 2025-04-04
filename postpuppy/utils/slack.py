import logging

from slack_bolt.async_app import AsyncAck
from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient

from postpuppy.utils.emails import send_verification_link
from postpuppy.utils.env import env
from postpuppy.utils.langs import LANGUAGES
from postpuppy.views.home import generate_home
from postpuppy.views.settings import generate_settings

app = AsyncApp(token=env.slack_bot_token, signing_secret=env.slack_signing_secret)


@app.event("app_home_opened")
async def update_home_tab(client: AsyncWebClient, event, logger):
    user_id = event["user"]
    view = await generate_home(user_id)
    await client.views_publish(user_id=user_id, view=view)


@app.action("open_settings")
async def open_settings(ack: AsyncAck, body, client: AsyncWebClient):
    await ack()
    user_id = body["user"]["id"]
    view = await generate_settings(user_id)
    await client.views_open(trigger_id=body["trigger_id"], view=view)


@app.action("channels_select")
async def channels_callback(ack: AsyncAck, body, client: AsyncWebClient):
    await ack()
    user_id = body["user"]["id"]
    view = body["view"]
    actions = view["state"]["values"]
    selected_channels = actions["channels"]["channels_select"]["selected_conversations"]

    user = await env.db.user.find_first(where={"id": user_id})
    if not user:
        return
    current_channels = user.subscribedChannels or []
    new_channels = [
        channel for channel in selected_channels if channel not in current_channels
    ]
    removed_channels = [
        channel for channel in current_channels if channel not in selected_channels
    ]

    language = LANGUAGES.get(user.language, LANGUAGES["dog"])
    lang = language["utils.slack"]

    for channel in new_channels:
        try:
            await env.slack_client.chat_postMessage(
                channel=channel,
                icon_emoji=language["icon_emoji"],
                username=language["display_name"],
                text=lang["setup"],
            )
        except Exception as e:
            logging.error(f"Failed to send message to {channel} ({user_id}\n{e}")
            blocks = language["setup_failed"]["blocks"]
            blocks[0]["text"]["text"] = blocks[0]["text"]["text"].format(channel)
            await env.slack_client.chat_postMessage(
                channel=user_id,
                icon_emoji=language["icon_emoji"],
                username=language["display_name"],
                text=lang["setup_failed"]["text"].format(channel),
                blocks=blocks,
            )

    for channel in removed_channels:
        try:
            await env.slack_client.chat_postMessage(
                channel=channel,
                icon_emoji=language["icon_emoji"],
                username=language["display_name"],
                text=lang["disabled"]["text"],
                blocks=lang["disabled"]["blocks"],
            )
        except Exception as e:
            logging.error(
                f"Failed to send message to removed channel {channel} ({user_id}\n{e}"
            )

    await env.db.user.update(
        where={"id": user_id}, data={"subscribedChannels": {"set": selected_channels}}
    )


@app.view("settings_callback")
async def settings_callback(ack: AsyncAck, body, client: AsyncWebClient):
    user_id = body["user"]["id"]
    view = body["view"]
    actions = view["state"]["values"]
    logging.info(actions)
    email: str = actions["email"]["email"]["value"]
    language = actions["language"]["language_select"]["selected_option"]["value"]

    user = await env.db.user.find_first(where={"id": user_id})

    if not user:
        return await ack(
            {"response_action": "errors", "errors": {"email": "User not found"}}
        )

    if not email:
        return await ack(
            {"response_action": "errors", "errors": {"email": "Email cannot be empty"}}
        )

    if user.language != language:
        await env.db.user.update(where={"id": user_id}, data={"language": language})
        await ack()
        lang = LANGUAGES.get(language, LANGUAGES["dog"])
        await client.chat_postMessage(
            icon_emoji=lang["icon_emoji"],
            username=lang["display_name"],
            channel=user_id,
            text=f"I'm now going to talk like a {language}",
        )

    if user.email == email and user.verifiedEmail:
        await ack()
        return await client.views_publish(
            user_id=user_id, view=await generate_home(user_id)
        )
    await ack()

    language = LANGUAGES.get(user.language, LANGUAGES["dog"])
    lang = language["utils.slack"]

    await env.db.user.update(
        where={"id": user_id},
        data={
            "email": email,
            "verifiedEmail": False,
            "emailSignature": None,
            "emailSignatureExpiry": None,
            "viewerUrl": None,
            "apiUrl": None,
        },
    )
    await send_verification_link(user_id, email, language)
    await client.chat_postMessage(
        channel=user_id,
        icon_emoji=language["icon_emoji"],
        username=language["display_name"],
        text=lang["verification_sent"]["text"],
        blocks=lang["verification_sent"]["blocks"],
    )

    return await client.views_publish(
        user_id=user_id, view=await generate_home(user_id)
    )


@app.action("link")
async def link_callback(ack: AsyncAck, body, client: AsyncWebClient):
    await ack()


@app.action("mail")
async def mail_callback(ack: AsyncAck, body, client: AsyncWebClient):
    await ack()
    user_id = body["user"]["id"]
    user_info = await client.users_info(user=user_id)

    email = user_info.get("user", {}).get("profile", {}).get("email")
    user = await env.db.user.find_first(where={"id": user_id})
    if not user or not email:
        return await ack(
            {"response_action": "errors", "errors": {"email": "User not found"}}
        )
    language = LANGUAGES.get(user.language, LANGUAGES["dog"])

    await send_verification_link(user_id, email, language)
