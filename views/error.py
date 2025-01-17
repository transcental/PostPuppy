def generate_error(error: str):
    return {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Error"},
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": ":neodog_notice: Error"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Oops, this shouldn't happen. Please message <@U054VC2KM9P> with the following message: `{error}`",
                },
            },
        ],
    }
