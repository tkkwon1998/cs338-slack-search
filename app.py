import os
from slack_bolt import App
import re

from google_searcher import *
from topic_extractor import *
from utility import *


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

# Check keys
# print(f'\n||{os.environ["SLACK_BOT_TOKEN"]}||\n')
# print(f'\n||{os.environ["SLACK_SIGNING_SECRET"]}||\n')


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


# Old "what" handler. Kept for reference.
# @app.message(re.compile('^[Ww]hat\s'))
# def wiki_link(message, say):
#     say('Matched')
#     query = message["text"][8:]
#     query += " Wikipedia"

#     result = google_search(query, GOOGLE_API_KEY, CSE_ID)

#     link = result["items"][0]["link"]

#     say(link)


# New "what" handler.
# Always grabs the last word in the sentence.
@app.message(re.compile('^[Ww]hat\s'))
def what_handler(message, say):

    # Word to be searched. Takes last word from input sentence.
    query = message["text"].split()[-1]

    # Build up string to be googled. Query is repeated twice to highlight it.
    # https://www.lifewire.com/how-to-search-specific-domain-in-google-3481807
    search_string = f'site:en.wikipedia.org {query} {query}'

    say(f'You asked about: "{query}." Thinking...')

    keywords, topics = definition(message, say)
    
    # https://stackoverflow.com/questions/12453580/how-to-concatenate-items-in-a-list-to-a-single-string
    topics_str = ' '.join(topics)
    search_string = f'{search_string} {topics_str}'

    # See final search_string in terminal
    pprint(search_string)

    # Get full search results
    result = google_search(search_string, GOOGLE_API_KEY, CSE_ID)

    # Take link to first result
    link = result["items"][0]["link"]

    say(link)


# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))





