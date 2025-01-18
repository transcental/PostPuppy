import logging
from typing import Optional

from utils.env import env


async def get_shipments(
    user_id: str, api_url: str, handle_error: bool = True
) -> Optional[list[dict]]:
    try:
        async with env.aiohttp_session.get(api_url) as response:
            data = await response.json()
            return data
    except Exception as e:
        if handle_error:
            await env.slack_client.chat_postMessage(
                channel=user_id,
                text=f"Something went wrong when fetching your shipments. Please check that your URL is correct in the settings. If you're sure and this keeps happening, forward this message to <@U054VC2KM9P>\n```{e}```\nError occurred in `utils/shipment.py`.",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Something went wrong when fetching your shipments. Please check that your URL is correct in the settings. If you're sure and this keeps happening, forward this message to <@U054VC2KM9P>",
                        },
                        "accessory": {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Settings"},
                            "action_id": "open_settings",
                        },
                    },
                    {"type": "divider"},
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"```{e}```"},
                    },
                    {"type": "divider"},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Error occurred in `utils/shipment.py`.",
                        },
                    },
                ],
            )
        return None


def find_diff(old: list[dict], new: list[dict]):
    diffs = []
    logging.info(f"Old: {type(old)}")
    old = old or []
    new = new or []
    old_shipments = {shipment.get("id"): shipment for shipment in old}
    new_shipments = {shipment.get("id"): shipment for shipment in new}

    all_ids = set(old_shipments.keys()).union(new_shipments.keys())
    for shipment_id in all_ids:
        msg = ""
        pub_msg = ""
        old_shipment = old_shipments.get(shipment_id, {})
        new_shipment = new_shipments.get(shipment_id, {})

        if old_shipment and not new_shipment:
            # shipment was removed
            msg = f':neodog_sob: Your order of *"{old_shipment.get("title", shipment_id)}"* has been cancelled'
        elif new_shipment and not old_shipment:
            # shipment was created
            msg = f':neodog_box: Shipment of *"{new_shipment.get("title", shipment_id)}"* on the way! _({new_shipment.get("type_text", new_shipment.get("type", "unknown_status").replace("_", "").title())}!)_'
        else:
            # shipment was updated
            updated_keys = []
            for key in old_shipment:
                if key not in new_shipment:
                    updated_keys.append(key)
                elif old_shipment[key] != new_shipment[key]:
                    updated_keys.append(key)

            for key in new_shipment:
                if key not in old_shipment:
                    updated_keys.append(key)

            for key in updated_keys:
                if (
                    ("tracking_number" in key or "tracking_link" in key)
                    and "shipped" in key
                    and new_shipment.get("shipped", False)
                ):
                    pub_msg = f':neodog_laptop_notice: *"{new_shipment.get("title", shipment_id)}"* has been shipped! And guess what! You can track it too! Visit my <slack://app?team=T0266FRGM&id={env.slack_app_id}|app home> to track it!'
                    msg = f':neodog_laptop_notice: Your *"{new_shipment.get("title", shipment_id)}"* has been shipped! You can track it <{new_shipment.get("tracking_link") or f"https://parcelsapp.com/en/tracking/{new_shipment.get("tracking_number")}"}|here>'

                elif (
                    "tracking_number" in key and new_shipment.get("tracking_number")
                ) or ("tracking_link" in key and new_shipment.get("tracking_link")):
                    pub_msg = f':neodog_laptop_notice: Your *"{new_shipment.get("title", shipment_id)}"* can be tracked! Visit my <slack://app?team=T0266FRGM&id={env.slack_app_id}|app home> to track it!'
                    msg = f':neodog_laptop_notice: Your *"{new_shipment.get("title", shipment_id)}"* can be tracked <{new_shipment.get("tracking_link") or f"https://parcelsapp.com/en/tracking/{new_shipment.get("tracking_number")}"}|here>'

                elif "type_text" in key and new_shipment.get("type_text"):
                    msg = f':neodog_notice: Your *"{new_shipment.get("title", shipment_id)}"* is now {new_shipment.get("type_text")}!'

                elif "description" in key and old_shipment.get(
                    "description"
                ) != new_shipment.get("description"):
                    msg = f':neodog_notice: The description of your *"{new_shipment.get("title", shipment_id)}"* has been updated to {"\n".join(new_shipment.get("description", ""))}!'

                else:
                    msg = f':neodog_notice: Your *"{new_shipment.get("title", shipment_id)}"* has been updated!'
        if msg:
            diffs.append({"msg": msg, "pub_msg": pub_msg or msg})

    return diffs or None
