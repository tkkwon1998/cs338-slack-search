# Homepage view JSON
# https://api.slack.com/reference/block-kit
# https://app.slack.com/block-kit-builder/

import json
from utility import *

# Wrapped in a function for modularity.
def get_homepage_view():

    view={
            "type": "home",
            "callback_id": "home_view",

            # body of the view
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Welcome to the Slack Search Bot Homepage!* :mag_right: :eyes: :male-detective:"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Slack Search Bot provides accurate, context-driven info on topics of interests, putting the power of the Web at your fingertips without ever needing to leave Slack! This page serves as documentation of the various commands the bot responds to. To utilize the full power of Slack Search Bot, check out the configuration options at the bottom!"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Command Documentation*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Angle brackets denote words that you fill in. For example, in the commands below you would replace `<query word>` with the word you want to search, whether that be 'cat' or 'apple'."
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "`<query word>??`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "Perform a *context-driven search* on the single word `<query word>`. Context-driven searches pull context out of recent messages sent to the channel to aid in disambiguation. They are good for pulling summary information. So if you want an overview of what a _current_ (in the context of, say, electricity) is, this is the command to use. A more specific question, like 'What is George Washington's birthday?' is best left to the next command."
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "`<query sentence>???`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "Perform a *short-answer search* using `<query sentence>`, which should be an entire sentence in natural language. For example, it could be 'What is George Washington's birthday?'"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Configuration Options*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Utilize the full power of Slack Search Bot by configuring these options to the needs of your Slack workspace."
                    },
                    "accessory": {
                        "type": "checkboxes",
                        "options": get_checkboxes_options_ar(), 
                        # "initial_options": already_checked, # Now set at the end only if it should be checked; kept here for reference.
                        "action_id": "config-checkboxes"
                    }
                }
            ]
        }

    # Code to check whether checkboxes should be checked by default:
    # See https://api.slack.com/reference/block-kit/block-elements#checkboxes
    with open("config.json") as config_file:
        config = json.load(config_file)

        if config["use_channel_topics"]:
            view["blocks"][-1]["accessory"]["initial_options"] = get_checkboxes_options_ar()


    

    return view


# Wrapper to return options dictionary for the checkboxes accessory.
# Might be used in both the options and initial_options fields, so broken
# out for modularity.
# This will have to be updated if we add more config options.
def get_checkboxes_options_ar():
    return [
                {
                    "text": {
                        "type": "mrkdwn",
                        "text": "Use channel topics as search context."
                    },
                    "description": {
                        "type": "mrkdwn",
                        "text": "E.g., if you have 'computer science' as the channel topic, it will use that as additional context beyond what is drawn from the conversation itself."
                    },
                    "value": "value-0"
                }
            ]