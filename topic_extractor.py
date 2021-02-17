import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import datetime
from nltk import tokenize
from operator import itemgetter
import math
from nltk.corpus import stopwords
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer


endpoint = "entries"
language_code = "en-us"


stop_words = set(stopwords.words('english'))

# Currently at today, but will change, for testing -- set to when script runs
today = datetime.datetime.today().date()
today_epoch = datetime.datetime(today.year, today.month, today.day).timestamp()
today_epoch = datetime.datetime.now().timestamp()


def get_messages(message):
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    channel_id = message["channel"]

    try:
        result = client.conversations_history(channel=channel_id, inclusive=True, oldest=today_epoch)

        conversation_history = result["messages"]
        text = ""
        list_form = []

        # 'bot_id'
        for s in conversation_history:
            try:
                # Filter out the slackbot
                if s['type'] == 'message':
                    text += s['text'] + " "
                    list_form.append(s['text'])
            except:
                continue
        text = text[:-1]

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

    # Just for testing
    # keywords = extract_keywords(test)
    # say("The keywords are: {}".format(keywords))

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


# Junk code
    # Old Oxford Dictionary code. Kept for reference.
    #     url = "https://od-api.oxforddictionaries.com/api/v2/" + endpoint + "/" + language_code + "/" + word_id.lower()
    #     r = requests.get(url, headers={"app_id": app_id, "app_key": app_key})
    #     # print("code {}\n".format(r.status_code))
    #     # print("text \n" + r.text)
    #     json_ret = r.json()
    #     results = json_ret["results"]

    #     say("There is/are " + str(len(results)) + " result(s).")
    #     for i in range(0, len(results)):
    #         result = results[i]
    #         lexical_entries = result["lexicalEntries"]
    #         say("There is/are " + str(len(lexical_entries)) + " lexical entry/entries in result " + str(i + 1) + ".")
    #         for j in range(0, len(lexical_entries)):
    #             entries = lexical_entries[j]['entries']
    #             say("There is/are " + str(len(entries)) + " entry/entries in lexical entry " + str(j + 1) + ".")
    #             for k in range(0, len(entries)):
    #                 senses = entries[k]['senses']
    #                 say("There is/are " + str(len(senses)) + " sense(s) in entry " + str(k + 1) + ".")
    #                 for senses_ind in range(0, len(senses)):
    #                     defs = senses[senses_ind]['definitions']
    #                     say("There is/are " + str(len(defs)) + " definition(s) in sense " + str(senses_ind + 1) + ".")
    #                     for def_ind in range(0, len(defs)):
    #                         say(str(def_ind + 1) + ": " + defs[def_ind])
    # else:
    #     say(f"I don't know man.")


# @app.message("Why")
# def idk(message, say):
#     user = message['user']
#     say(f"I don't know man.")


# @app.event("app_mention")
# def event_test(body, say, logger):
#     logger.info(body)
#     say("What's up?")

# def extract_keywords(text):
#     total_words = text.split()
#     total_word_length = len(total_words)
#
#     total_sentences = tokenize.sent_tokenize(text)
#     total_sent_len = len(total_sentences)
#
#     tf_score = {}
#     for each_word in total_words:
#         each_word = each_word.replace('.', '')
#         if each_word not in stop_words:
#             if each_word in tf_score:
#                 tf_score[each_word] += 1
#             else:
#                 tf_score[each_word] = 1
#
#     tf_score.update((x, y / int(total_word_length)) for x, y in tf_score.items())
#
#     # Check if a word is there in sentence list
#     def check_sent(word, sentences):
#         final = [all([w in x for w in word]) for x in sentences]
#         sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
#         return int(len(sent_len))
#
#     # Step 4: Calculate IDF for each word
#     idf_score = {}
#     for each_word in total_words:
#         each_word = each_word.replace('.', '')
#         if each_word not in stop_words:
#             if each_word in idf_score:
#                 idf_score[each_word] = check_sent(each_word, total_sentences)
#             else:
#                 idf_score[each_word] = 1
#
#     # Performing a log and divide
#     idf_score.update((x, math.log(int(total_sent_len) / y)) for x, y in idf_score.items())
#
#     tf_idf_score = {key: tf_score[key] * idf_score.get(key, 0) for key in tf_score.keys()}
#
#     def get_top_n(dict_elem, n):
#         result = sorted(dict_elem.items(), key=itemgetter(1), reverse=True)[:n]
#         return result
#
#     ret = []
#     for i in get_top_n(tf_idf_score, 5):
#         ret.append(i[0])
#     return ret


# Start your app
# if __name__ == "__main__":
#     app.start(3000)