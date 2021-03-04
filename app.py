import os
from slack_bolt import App
import re
import spacy
import json
import urllib3

from google_searcher import *
from topic_extractor import *
from utility import *
from homepage_view import *


# File containing all keys
f = open("keys.txt", "r")

# WARNING: Make sure that keys.txt has empty lines after the 
# lines with strings in them. For some reason, if you don't
# have empty lines, it will cut off the last letter
# of the string on the last line.
GOOGLE_API_KEY =                        f.readline()[:-1]
CSE_ID =                                f.readline()[:-1]
os.environ['SLACK_BOT_TOKEN'] =         f.readline()[:-1]
os.environ['SLACK_SIGNING_SECRET'] =    f.readline()[:-1]


# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Listens to incoming messages that contain "hello"
@app.message("Hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>!")


@app.message(re.compile('^:query\s'))
def google_query(message, say):
    msg = message["text"][len(":query "):]

    # Get full search results
    result = google_search(msg, GOOGLE_API_KEY, CSE_ID)

    # Take link to first result
    link = result["items"][0]["link"]

    say(link)


# New "what" handler.
# Always grabs the last word in the sentence.
@app.message(re.compile('^[Ww]hat\s'))
def what_handler(message, say, client):

    # Word to be searched. Takes last word from input sentence.
    # query = message["text"].split()[-1]

    nlp = spacy.load('en_core_web_sm')
    doc = nlp(message["text"])

    sub_toks = [tok for tok in doc if (tok.dep_ == "nsubj")]
    obj_toks = [tok for tok in doc if (tok.dep_ == "pobj")]

    # Checks if definition is part of the sentence before processing it.
    if 'definition' in sub_toks[0].text:
        obj = obj_toks[0].text.lower()
    else:
        return

    say(f'You asked about: "{obj}." Thinking...')

    query = "intitle:" + obj

    # Build up string to be googled. Query is repeated twice to highlight it.
    # https://www.lifewire.com/how-to-search-specific-domain-in-google-3481807
    search_string = f'site:en.wikipedia.org {query}'

    # ---------------Config code start
    # Append channel topic if "use_channel_topics" is True.
    # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
    with open("config.json") as config_file:
        config = json.load(config_file)

        if config["use_channel_topics"]:
            # https://slack.dev/bolt-python/concepts#web-api
            # https://api.slack.com/methods/conversations.info

            # NB: Because it is Python and not JS (presumably), it is 
            # conversations_info instead of conversations.info
            channel_info = client.conversations_info(
                channel =   message["channel"], # Conversation ID
                token =     os.environ['SLACK_BOT_TOKEN'] # OAuth token
            )

            channel_topic = channel_info["channel"]["topic"]["value"]
            search_string = f'{search_string} {channel_topic}'

            say("Using channel topic for additional context.")
    # ---------------Config code end

    topics = definition(message, say)
    
    # https://stackoverflow.com/questions/12453580/how-to-concatenate-items-in-a-list-to-a-single-string
    if obj not in topics:
        search_string += " " + obj
    topics_str = ' '.join(topics)
    search_string = f'{search_string} {topics_str}'

    # See final search_string in terminal
    pprint(search_string)

    # Get full search results
    result = google_search(search_string, GOOGLE_API_KEY, CSE_ID)

    # Take link to first result
    link = result["items"][0]["link"]

    say(link)
    say("If this was not the result you wanted, you can also submit a google query by typing :query before your query.")


# Really good documentation:
# https://slack.dev/bolt-python/concepts#action-listening
@app.action("config-checkboxes")
def config_checkbox_handler(ack, body, client):
    '''
    body: Big dictionary containing all the info about the action.
    ack: You must call ack() in the handler to acknowledge the action.
    '''

    ack()

    # Will update this to True if the checkbox is actually selected.
    use_channel_topics = False

    # Array containing all selected checkboxes:
    selected_checkboxes = body["actions"][0]["selected_options"]

    for checkbox in selected_checkboxes:
        # This check isn't strictly necessary since we don't have multiple config options,
        # but if we add more we can build off this. (Add checks for other config options.)
        if "Use channel topics as search context." in checkbox["text"]["text"]:
            use_channel_topics = True

    # Update JSON "database":
    # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
    config = {}
    config["use_channel_topics"] = use_channel_topics

    with open('config.json', 'w') as outfile:
        json.dump(config, outfile)
    
    




@app.event("app_home_opened")
def display_home_tab(client, event, logger):

    try:
        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
        # the user that opened your app's app home
        user_id=event["user"],
        # the view object that appears in the app home
        # See the homepage_view.py file.
        view=get_homepage_view()
        )
  
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


# Britannica API code:
@app.message(re.compile("^[Ww]hat\sis|^[Ww]here\sis|^[Ww]hen\sis|^[Ww]ho\sis|^[Hh]ow\sis"))
def ask_whatIs(message, say):
    question = message["text"]
    http = urllib3.PoolManager()
    r = http.request('GET',
                    'https://rdc1nf9jza.execute-api.us-east-1.amazonaws.com/api/qna',
                    headers={
                        'x-api-key': '9HeBB23LR4a8mruNNf3kq17fFuR9b4JP1q5KSMCC'},
                    fields={'search_string': question})
    result_json = json.loads(r.data)
    print(result_json)
    say(f'You asked: "{question} " Thinking...')
    if "longAnswer" not in result_json:
        say("Sorry, we couldn't find an exact answer. Maybe, this is what you are looking for:")
        say(result_json["mendelResults"][0]["paragraph"])
    else:
        answer = result_json["longAnswer"]
        sentence_split = answer.split('. ')
        say(sentence_split[0] + '.')


# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))

