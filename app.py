import os
# Use the package we installed
from slack_bolt import App
import re

print("Up and running.")

##### START OF GOOGLE API CODE #####

from googleapiclient.discovery import build
import json

my_api_key = "<fill me in>"
my_cse_id = "<fill me in>"

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res

# result = google_search("Coffee", my_api_key, my_cse_id)

##### START OF SLACK API CODE #####

os.environ['SLACK_BOT_TOKEN'] = "<fill me in>"
os.environ['SLACK_SIGNING_SECRET'] = "<fill me in>"

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)


# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    print('About to send message.')
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>!")

@app.message(re.compile('^[Ww]hat\s'))
def wiki_link(message, say):
    say('Matched')
    # say(message["text"])
    query = message["text"][8:]
    query += " Wikipedia"

    result = google_search(query, my_api_key, my_cse_id)

    link = result["items"][0]["link"]

    say(link)
    
          

# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))





