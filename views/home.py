import logging

from utils.env import env


async def generate_home(user_id: str):
    user_data = await env.db.user.find_first(where={"id": user_id})
    if not user_data:
        user_data = await env.db.user.create({"id": user_id})

    url = user_data.viewerUrl
    if not url or not user_data.apiUrl:
        return {
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": ":neodog_box: Post Puppy",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "hai! i'm your friendly puppy who loves post nya~! i can help you keep track of your shipments from Hack Club :3\n\nyou haven't set up your viewer URL yet, please do so in the settings!",
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
                        "text": ":neodog_notice: Post Puppy",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "arf, arf!\noh no! it looks like i can't fetch your shipments right now :c\nplease check your settings and make sure your URL is correct!",
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
        block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{':mailbox_with_mail:' if shipment.get('shipped', False) else ':mailbox:'} {shipment.get('icon')} *{shipment.get('title').replace('_', ' ').title()}* - _{shipment.get('type_text', '')}_\n{'\n'.join(shipment.get('description', ''))}",
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
