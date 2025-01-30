import logging

from postpuppy.utils.env import env
from postpuppy.utils.langs import LANGUAGES
from postpuppy.utils.signing import get_viewer_signature


async def generate_home(user_id: str):
    user_data = await env.db.user.find_first(where={"id": user_id})
    if not user_data:
        user_info = await env.slack_client.users_info(user=user_id)
        email = user_info["user"]["profile"]["email"]
        viewer_url = await get_viewer_signature(email)
        api_url = viewer_url.replace("shipments", "jason")

        user_data = await env.db.user.create(
            {
                "id": user_id,
                "viewerUrl": viewer_url,
                "apiUrl": api_url,
                "email": email,
                "verifiedEmail": True,
            }
        )
        user_data = await env.db.user.find_first(where={"id": user_id})
        if not user_data:
            return {
                "type": "home",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": ":neodog_notice: Post Puppy",
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "oh no! i can't find your user data, please try again!",
                        },
                    },
                ],
            }

    url = user_data.viewerUrl
    language = LANGUAGES.get(user_data.language, LANGUAGES["dog"])["views.home"]

    if not url or not user_data.apiUrl:
        return {
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": language["heading"],
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": language["description"],
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "get started"},
                            "action_id": "open_settings",
                            "style": "primary",
                        }
                    ],
                },
            ],
        }

    try:
        async with env.aiohttp_session.get(user_data.apiUrl) as response:
            data = await response.json()
    except Exception as e:
        logging.error(e)
        return {
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": language["error_heading"],
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": language["error_description"],
                    },
                },
                {"type": "divider"},
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Open Settings"},
                            "style": "primary",
                            "action_id": "open_settings",
                        }
                    ],
                },
            ],
        }

    total_fulfilled = len(list(filter(lambda s: s.get("shipped", False), data)))

    shipments = []
    for shipment in data:
        desc = shipment.get("description", [])
        list_desc = [desc] if type(desc) is str else desc
        block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{':mailbox_with_mail:' if shipment.get('shipped', False) else ':mailbox:'} {shipment.get('icon')} *{shipment.get('title').replace('_', ' ').title()}* - _{shipment.get('type_text', '')}_\n{'\n'.join(list_desc)}",
            },
        }
        if shipment.get("tracking_number") or shipment.get("tracking_link"):
            block["accessory"] = {
                "type": "button",
                "text": {"type": "plain_text", "text": "Track"},
                "action_id": "link",
                "url": shipment.get("tracking_link")
                or f"https://parcelsapp.com/en/tracking/{shipment.get('tracking_number')}",
            }

        shipments.append(block)
        shipments.append({"type": "divider"})

    return {
        "type": "home",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": ":neodog_box: Shipment Stalker"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Welcome to Shipment Stalker! Here, you can view all your shipments from Hack Club.\n\nYou have *{total_fulfilled}* fulfilled shipments and *{len(data) - total_fulfilled}* pending shipments!",
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Open Settings"},
                    "action_id": "open_settings",
                },
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Shipments:*"}},
            {"type": "divider"},
            *shipments,
        ],
    }
