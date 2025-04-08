import json
import logging

from postpuppy.utils.env import env
from postpuppy.utils.langs import LANGUAGES
from postpuppy.utils.logging import send_heartbeat


async def get_shipments(
    user_id: str, api_url: str, handle_error: bool = True
) -> list[dict]:
    try:
        async with env.aiohttp_session.get(api_url) as response:
            data = await response.json()
            return data or [{}]
    except Exception as e:
        if handle_error:
            await env.slack_client.chat_postMessage(
                channel=user_id,
                text=f"Something went wrong when fetching your shipments. Please check that your email is correct in the settings. If you're sure and this keeps happening, forward this message to <@U054VC2KM9P>\n```{e}```\nError occurred in `utils/shipment.py`.",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Something went wrong when fetching your shipments. Please check that your email is correct in the settings. If you're sure and this keeps happening, forward this message to <@U054VC2KM9P>",
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
        return [{}]


async def find_diff(old: list[dict], new: list[dict], language: dict):
    diffs = []
    old = old or []
    new = new or []
    old_shipments = {shipment.get("title"): shipment for shipment in old}
    new_shipments = {shipment.get("title"): shipment for shipment in new}

    all_ids = set(old_shipments.keys()).union(new_shipments.keys())
    lang = language.get("utils.shipments", LANGUAGES["dog"]["utils.shipments"])

    for shipment_id in all_ids:
        logging.info(f"Checking shipment {shipment_id}")
        msg = ""
        pub_msg = ""
        old_shipment = old_shipments.get(shipment_id, {})
        new_shipment = new_shipments.get(shipment_id, {})

        if old_shipment and not new_shipment:
            # shipment was removed
            msg = lang["deleted_shipment"].format(
                old_shipment.get("title", shipment_id)
            )
        elif new_shipment and not old_shipment:
            # shipment was created
            await send_heartbeat(
                "New shipment found",
                [
                    f"```{json.dumps(old_shipment, indent=2)}```",
                    f"```{json.dumps(new_shipment, indent=2)}```",
                ],
            )
            msg = lang["new_shipment"].format(
                new_shipment.get("title", shipment_id),
                new_shipment.get(
                    "type_text",
                    new_shipment.get("type", "unknown_status")
                    .replace("_", " ")
                    .title(),
                ),
                "\n- ".join(new_shipment.get("description", [])),
            )
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

            if not updated_keys:
                continue

            if new_shipment.get("shipped", False) and (
                "tracking_number" in updated_keys or "tracking_link" in updated_keys
            ):
                pub_msg = lang["new_shipment_with_tracking"]["pub_msg"].format(
                    new_shipment.get("title", shipment_id),
                    "\n- ".join(new_shipment.get("description", [])),
                )

                msg = lang["new_shipment_with_tracking"]["msg"].format(
                    new_shipment.get("title", shipment_id),
                    new_shipment.get("tracking_link")
                    or f"https://parcelsapp.com/en/tracking/{new_shipment.get('tracking_number')}",
                    "\n- ".join(new_shipment.get("description", [])),
                )

            elif (
                "tracking_number" in updated_keys
                and new_shipment.get("tracking_number")
            ) or (
                "tracking_link" in updated_keys and new_shipment.get("tracking_link")
            ):
                pub_msg = (
                    f':neodog_laptop_notice: wrrf, wrrf, wrrrrf!! your *"{new_shipment.get("title", shipment_id)}"* can be tracked, arf, arf! '
                    f"i found a tracking bone for you! it's in my  <slack://app?team=T0266FRGM&id={env.slack_app_id}|bed> :3"
                )
                msg = lang["new_shipment_with_tracking"]["msg"].format(
                    new_shipment.get("tracking_link")
                    or f"https://parcelsapp.com/en/tracking/{new_shipment.get('tracking_number')}",
                    new_shipment.get("title", shipment_id),
                )

            elif "type_text" in updated_keys and new_shipment.get("type_text"):
                msg = lang["type_text_updated"].format(
                    new_shipment.get("title", shipment_id),
                    new_shipment.get("type_text", "up to something").lower(),
                )

            elif "description" in updated_keys and old_shipment.get(
                "description"
            ) != new_shipment.get("description"):
                msg = lang["description_updated"].format(
                    new_shipment.get("title", shipment_id),
                    "\n- ".join(new_shipment.get("description", "")),
                )

            elif "shipped" in updated_keys and new_shipment.get("shipped"):
                msg = lang["shipped"].format(new_shipment.get("title", shipment_id))

            else:
                msg = lang["unknown_update"].format(
                    new_shipment.get("title", shipment_id)
                )
        if msg:
            diffs.append({"msg": msg, "pub_msg": pub_msg or msg})

    return diffs or None
