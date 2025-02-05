from postpuppy.utils.env import env


LANGUAGES = {
    "dog": {
        "display_name": "Post Puppy",
        "icon_emoji": ":neodog_box:",
        "utils.checker": {
            "cant_send": {
                "text": "haiii :3\nlooks like i can't send to channel <#{}>, please make sure i'm in the channel uwu",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "haiii :3\nlooks like i can't send to <#{}>, please make sure you added me to the channel uwu :3",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "_wrrf, wrrrrrrf (sad barking noises)_",
                            }
                        ],
                    },
                ],
            }
        },
        "utils.shipments": {
            "deleted_shipment": ':neodog_sob: arf arf~ order of *"{}"* has been cancelled :c i hope that\'s okay master! _wrrf, wrrf!_',
            "new_shipment": ':neodog_box: arf arf~ your package, *"{}"*, is on its way, wrrf! i found these fancy terms, not sure what it means though, rrf! _({}!)_\noh, and this is what\'s inside!\n{}',
            "new_shipment_with_tracking": {
                "pub_msg": f':neodog_laptop_notice: "wrrf! your *"{{}}"*, is on its way, wag wag! and guess what, fren! you can track it too, tail wags! visit my <slack://app?team=T0266FRGM&id={env.slack_app_id}|bed> to see where it\'s at, woof woof!! 🐾\npsst, it has this stuff inside!\n{{}}',
                "msg": ':neodog_laptop_notice: wrrf! wrrf! your *"{}"* is on its way, wag wag! i think there\'s a tracking bone on my pillow\n<{}|throw bone>\na little birdy told me it has these things inside\n{}',
            },
            "updated_shipment_with_tracking": {
                "pub_msg": f':neodog_laptop_notice: wrrf, wrrf, wrrrrf!! your *"{{}}"* can be tracked, arf, arf!\ni found a tracking bone for you! it\'s in my  <slack://app?team=T0266FRGM&id={env.slack_app_id}|bed> :3',
                "msg": ':neodog_laptop_notice: _arf, arf!!_ i found a <{}|tracking bone> for your *"{}"* on my pillow! \n_wrrf, wrrf_',
            },
            "type_text_updated": ':neodog_notice: hey hey hey hey hey!!!! frien, it looks like your *"{}"* is now {}! :3',
            "description_updated": ':neodog_notice: woah, buddy! your *"{}"* has been updated to {}!!!!\nthat\'s amazing :D',
            "unknown_update": ':neodog_notice: sowwy, idk what happened, but your *"{}"* has been updated!!! _(excited barking)_',
        },
        "utils.slack": {
            "setup": "Wrrf, wrrf, wrrf!!!! wrrf!\n_hai! i'm watching your shipments for you now :3_",
            "setup_failed": {
                "text": "haiii :3\nlooks like i can't send to channel <#{}>, please make sure i'm in the channel uwu",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "haiii :3\nlooks like i can't send to <#{}>, please make sure you added me to the channel uwu :3",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "_wrrf, wrrrrrrf (sad barking noises)_",
                            }
                        ],
                    },
                ],
            },
            "disabled": {
                "text": ":neodog_sob: i'm not watching your shipments anymore :c\n_wrrf, wrrrrrrf (sad barking noises)_",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":neodog_sob: _arf! arf!_ i'm not watching your shipments anymore :c",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "_wrrf, wrrrrrrf (sad barking noises)_",
                            }
                        ],
                    },
                ],
            },
            "verification_sent": {
                "text": "i've sent you an email with a link to verify your email address! pwease check your inbox and click the link :3",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "i've sent you an email with a link to verify your email address! pwease check your inbox and click the link :3",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "wags tail excitedly at all those ships",
                            }
                        ],
                    },
                ],
            },
        },
        "utils.starlette": {
            "verified_slack": {
                "text": "Your email has been verified! You can now view your shipments",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Your email has been verified! You can now view your shipments",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "wags tail excitedly at all those ships",
                            }
                        ],
                    },
                ],
            }
        },
        "views.home": {
            "heading": ":neodog_box: Post Puppy",
            "description": "hai! i'm your friendly puppy who loves post nya~! i can help you keep track of your shipments from Hack Club :3\n\nyou haven't set up your viewer URL yet, please do so in the settings!",
            "error_heading": ":neodog_notice: Post Puppy",
            "error_description": "arf, arf!\noh no! it looks like i can't fetch your shipments right now :c\nplease check your settings and make sure your URL is correct!",
        },
    },
    "cat": {
        "display_name": "Correspondence Kitty",
        "icon_emoji": ":neocat_box:",
        "utils.checker": {
            "cant_send": {
                "text": "haiii :3\nlooks like i can't send to channel <#{}>, please make sure i'm in the channel uwu",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "haiii :3\nlooks like i can't send to <#{}>, please make sure you added me to the channel uwu :3",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "_meow, meoooooow (sad kitty noises)_",
                            }
                        ],
                    },
                ],
            }
        },
        "utils.shipments": {
            "deleted_shipment": ':neocat_sob: meow meow~ order of *"{}"* has been cancelled :c i hope that\'s okay master! _meow, meow!_',
            "new_shipment": ':neocat_box: meow meow~ your package, *"{}"*, is on its way, meow! i found these fancy terms, not sure what it means though, mrow! _({}!)_\noh, and this is what\'s inside!\n{}',
            "new_shipment_with_tracking": {
                "pub_msg": f':neocat_laptop_notice: "mrow! your *"{{}}"*, is on its way, purr purr! and guess what, fren! you can track it too, tail flick! visit my <slack://app?team=T0266FRGM&id={env.slack_app_id}|bed> to see where it\'s at, meow meow!! 🐾\npsst, it has this stuff inside!\n{{}}',
                "msg": ':neocat_laptop_notice: mrow! mrow! your *"{}"* is on its way, meow meow! i think there\'s a tracking fish on my pillow\n<{}|throw fish>\na little birdy told me it has these things inside\n{}',
            },
            "updated_shipment_with_tracking": {
                "pub_msg": f':neocat_laptop_notice: meow, meow, meoooow!! your *"{{}}"* can be tracked, meow meow!\ni found a tracking bone for you! it\'s in my  <slack://app?team=T0266FRGM&id={env.slack_app_id}|bed> :3',
                "msg": ':neocat_laptop_notice: _meow, meow!!_ i found a <{}|tracking fish> for your *"{}"* on my pillow! \n_purr, purrr_',
            },
            "type_text_updated": ':neocat_notice: hey hey hey hey hey!!!! frien, it looks like your *"{}"* is now {}! :3',
            "description_updated": ':neocat_notice: woah, buddy! your *"{}"* has been updated to {}!!!!\nthat\'s amazing :D',
            "unknown_update": ':neocat_notice: sowwy, idk what happened, but your *"{}"* has been updated!!! _(excited purring)_',
        },
        "utils.slack": {
            "setup": "Meow meow meoow!!!! mrow!\n_hai! i'm watching your shipments for you now :3_",
            "setup_failed": {
                "text": "haiii :3\nlooks like i can't send to channel <#{}>, please make sure i'm in the channel uwu",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "haiii :3\nlooks like i can't send to <#{}>, please make sure you added me to the channel uwu :3",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "_meow, meoooow (sad kitty noises)_",
                            }
                        ],
                    },
                ],
            },
            "disabled": {
                "text": ":neocat_sob: i'm not watching your shipments anymore :c\n_mrow, mrooow (sad kitty noises)_",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":neocat_sob: meow! meow!_ i'm not watching your shipments anymore :c",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "_meow, meooooow (sad kitty noises)_",
                            }
                        ],
                    },
                ],
            },
            "verification_sent": {
                "text": "i've sent you an email with a link to verify your email address! pwease check your inbox and click the link :3",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "i've sent you an email with a link to verify your email address! pwease check your inbox and click the link :3",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "purrs excitedly at all those ships",
                            }
                        ],
                    },
                ],
            },
        },
        "utils.starlette": {
            "verified_slack": {
                "text": "Your email has been verified! You can now view your shipments",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Your email has been verified! You can now view your shipments",
                        },
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "purrs excitedly at all those ships",
                            }
                        ],
                    },
                ],
            }
        },
        "views.home": {
            "heading": ":neocat_box: Correspondence Kitty",
            "description": "hai! i'm your friendly kitty who loves post nya~! i can help you keep track of your shipments from Hack Club :3\n\nyou haven't set up your viewer URL yet, please do so in the settings!",
            "error_heading": ":neocat_notice: Correspondance Kitty",
            "error_description": "meow, meow!\noh no! it looks like i can't fetch your shipments right now :c\nplease check your settings and make sure your URL is correct!",
        },
    },
}
