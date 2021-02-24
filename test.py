import json
import urllib3

http = urllib3.PoolManager()
r = http.request('GET',
                 'https://rdc1nf9jza.execute-api.us-east-1.amazonaws.com/api/qna',
                 headers={'x-api-key': '9HeBB23LR4a8mruNNf3kq17fFuR9b4JP1q5KSMCC'},
                 fields={'search_string': 'what is a binary tree'})

result_json = json.loads(r.data)

print(result_json)