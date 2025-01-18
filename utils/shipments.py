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
            msg = f':neodog_sob: arf arf~ order of *"{old_shipment.get("title", shipment_id)}"* has been cancelled :c i hope that\'s okay master! _wrrf, wrrf!_'
        elif new_shipment and not old_shipment:
            # shipment was created
            msg = f':neocat_box: arf arf~ your package, *"{new_shipment.get("title", shipment_id)}"*, is on its way, wrrf! i found these fancy terms, not sure what it means though, rrf! _({new_shipment.get("type_text", new_shipment.get("type", "unknown_status").replace("_", " ").title())}!)_'
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
                pub_msg = f':neodog_laptop_notice: "wrrf! your *"{new_shipment.get("title", shipment_id)}"*, is on its way, wag wag! and guess what, friend! you can track it too, tail wags! visit my <slack://app?team=T0266FRGM&id={env.slack_app_id}|bed> to see where it\'s at, woof woof!!1 🐾'

                msg = f':neodog_laptop_notice: wrrf! wrrf! your *"{new_shipment.get("title", shipment_id)}"* is on its way, wag wag! i think there\'s a tracking bone on my pillow\n<{new_shipment.get("tracking_link") or f"https://parcelsapp.com/en/tracking/{new_shipment.get("tracking_number")}"}|throw bone>'

            elif (
                "tracking_number" in updated_keys
                and new_shipment.get("tracking_number")
            ) or (
                "tracking_link" in updated_keys and new_shipment.get("tracking_link")
            ):
                pub_msg = (
                    f':neodog_laptop_notice: wrrf, wrrf, wrrrrf!! your *"{new_shipment.get("title", shipment_id)}"* can be tracked, arf, arf! '
                    f'i found a tracking bone for you! it\'s in my  <slack://app?team=T0266FRGM&id={env.slack_app_id}|bed> :3'
                )
                msg = f':neodog_laptop_notice: _arf, arf!!_ i found a <{new_shipment.get("tracking_link") or f"https://parcelsapp.com/en/tracking/{new_shipment.get("tracking_number")}"}|tracking bone> for your *"{new_shipment.get("title", shipment_id)}"* on my pillow! \n_wrrf, wrrf_'

            elif "type_text" in updated_keys and new_shipment.get("type_text"):
                msg = f':neodog_notice: hey hey hey hey hey!!!! friend, it looks like your *"{new_shipment.get("title", shipment_id)}"* is now {new_shipment.get("type_text", "up to something").lower()}! :3'

            elif "description" in updated_keys and old_shipment.get(
                "description"
            ) != new_shipment.get("description"):
                msg = (
                    f':neodog_notice: woah, buddy! your *"{new_shipment.get("title", shipment_id)}"* has been updated to '
                    f'{"\n".join(new_shipment.get("description", ""))}!!!!\nthat\'s amazing :D'
                )

            else:
                msg = f':neodog_notice: sowwy, idk what happened, but your *"{new_shipment.get("title", shipment_id)}"* has been updated!!! _(excited barking)_'
        if msg:
            diffs.append({"msg": msg, "pub_msg": pub_msg or msg})

    return diffs or None
