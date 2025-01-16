from utils.env import env
from views.error import generate_error

async def generate_settings(user_id: str):
    user = await env.db.user.find_first(where={"id": user_id})
    if not user:
        return generate_error("settings.py: User not found")

    url_input_block = [{
        "type": "input",
        "block_id": "viewerUrl",
        "element": {
            "type": "url_text_input",
            "action_id": "url_input",
            "placeholder": {
                "type": "plain_text",
                "text": "https://shipment-viewer.hackclub.com/dyn/shipments/orpheus@hackclub.com?signature=specialfancyalphanumericsequence"
            },
        },
        "label": {
            "type": "plain_text",
            "text": "Viewer URL"
        }
    }]
    
    if user.viewerUrl and user.apiUrl:
        url_input_block[0]["element"]["initial_value"] = user.viewerUrl

    return {
        "type": "modal",
        "callback_id": "settings_callback",
        "title": {
            "type": "plain_text",
            "text": "Settings"
        },
        "submit": {
            "type": "plain_text",
            "text": "Save"
        },
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":neodog_solder: Shipment Stalker Settings"
                }
            },
            *url_input_block,
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "You can find your Viewer URL by going to the <https://shipment-viewer.hackclub.com|Shipment Viewer>, signing in and copying the URL from the email :dinobox: Dinobox sends you."
                    }
                ]
            },
            {
    			"type": "section",
     			"block_id": "channels",
    			"text": {
    				"type": "mrkdwn",
    				"text": "Notification Channels"
    			},
    			"accessory": {
    				"type": "multi_conversations_select",
    				"placeholder": {
    					"type": "plain_text",
    					"text": "Select conversations to notify",
    					"emoji": True
    				},
                    "initial_conversations": user.subscribedChannels or [],
                    "action_id": "channels_select"
    			}
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "The channel Shipment Stalker will send notifications to when a shipment is updated or added."
                    }
                ]
            }
        ]
    }
