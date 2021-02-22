import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import datetime
from nltk.corpus import stopwords
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer


endpoint = "entries"
language_code = "en-us"


stop_words = set(stopwords.words('english'))

# Currently at today, but will change, for testing -- set to when script runs
# today = datetime.datetime.today().date()
# today_epoch = datetime.datetime(today.year, today.month, today.day).timestamp()
today_epoch = datetime.datetime.now().timestamp()

word_count_thresh = 150

def get_messages(message):
    global today_epoch
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    channel_id = message["channel"]

    try:
        result = client.conversations_history(channel=channel_id, inclusive=True, oldest=today_epoch)

        conversation_history = result["messages"]
        text = ""
        list_form = []

        word_count = 0
        for s_ind in range(len(conversation_history) - 1, -1, -1):
            s = conversation_history[s_ind]
            try:
                # Filter out the slackbot messages
                if s['type'] == 'message' and 'bot_id' not in s and s['client_msg_id'] != message['client_msg_id']:
                    text += s['text'] + " "
                    word_count += s['text'].count(" ") + 1
                    list_form.append(s['text'])
                # Try to only look at the 150 most recent words for the naive multiple context handing feature
                if word_count > word_count_thresh:
                    break
            except:
                continue
        text = text[:-1]

        # By default, assume topic is changing when a question is asked.
        today_epoch = datetime.datetime.now().timestamp()

        return text, list_form

    except SlackApiError as e:
        print("Error: {}".format(e))
        return None


def extract_topic(text_list):
    no_features = 1000

    # NMF is able to use tf-idf
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, use_idf=True, max_features=no_features, stop_words='english')
    tfidf = tfidf_vectorizer.fit_transform(text_list)
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()

    no_topics = 1
    nmf = NMF(n_components=no_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)

    def display_topics(model, feature_names, ntw):
        topics = []
        for topic_idx, topic in enumerate(model.components_):
            print("Topic {}:".format(topic_idx))
            keywords = [feature_names[i] for i in topic.argsort()[:-ntw - 1:-1]]
            topics.append(keywords)
            print(" ".join(keywords))
        return topics

    no_top_words = 5

    topics = display_topics(nmf, tfidf_feature_names, no_top_words)
    return topics


def definition(message, say):
    test, testl = get_messages(message)
    print(test)

    topics = extract_topic(testl)
    say("The topics are:")
    for i in range(0, len(topics)):
        ltopics = topics[i]
        ptopics = ""
        for j in ltopics:
            ptopics += j + ", "
        ptopics = ptopics[:-2]
        say("{}: {}".format(i + 1, ptopics))

    # keywords is just a list containing strings.
    # topics is a list containing a single entry. That entry is another list
    # containing the actual topic strings.
    return topics[0]

