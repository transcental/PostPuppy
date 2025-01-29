from postpuppy.utils.env import env
from postpuppy.utils.langs import LANGUAGES
from postpuppy.views.error import generate_error


async def generate_settings(user_id: str):
    user = await env.db.user.find_first(where={"id": user_id})
    if not user:
        return generate_error("settings.py: User not found")

    user_info = await env.slack_client.users_info(user=user_id)
    email = user.email or user_info["user"]["profile"]["email"]

    if not email:
        return generate_error("settings.py: Email not found (This is impossible)")

    return {
        "type": "modal",
        "callback_id": "settings_callback",
        "title": {"type": "plain_text", "text": "Settings"},
        "submit": {"type": "plain_text", "text": "Save"},
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":neodog_solder: post puppy settings",
                },
            },
            {
                "type": "input",
                "block_id": "email",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "email",
                    "initial_value": email,
                },
                "label": {"type": "plain_text", "text": "Email"},
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "This should be the email you use for the <https://shipment-viewer.hackclub.com|Shipment Viewer>! I'll send you a link to confirm that you own it :3",
                    }
                ],
            },
            {
                "type": "section",
                "block_id": "channels",
                "text": {"type": "mrkdwn", "text": "Barking Channels"},
                "accessory": {
                    "type": "multi_conversations_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select conversations to bark in",
                        "emoji": True,
                    },
                    "initial_conversations": user.subscribedChannels or [],
                    "action_id": "channels_select",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "The channel Post Puppy will bark in when a shipment is updated or added.",
                    }
                ],
            },
            {
                "type": "input",
                "block_id": "language",
                "element": {
                    "type": "static_select",
                    "initial_option": {
                        "text": {
                            "type": "plain_text",
                            "text": user.language.title() or "Dog",
                            "emoji": True,
                        },
                        "value": user.language or "dog",
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": lang.title(),
                                "emoji": True,
                            },
                            "value": lang,
                        }
                        for lang in LANGUAGES.keys()
                    ],
                    "action_id": "language_select",
                },
                "label": {"type": "plain_text", "text": "Language", "emoji": True},
            },
        ],
    }
