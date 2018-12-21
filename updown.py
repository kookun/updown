# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
import random

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = "xoxb-506274278966-508887151878-pLgkF3bWaIkBgqhaOBxYlwXt"
slack_client_id = "506274278966.508536991751"
slack_client_secret = "63c3b63b26ffd370727cd1803fc1394a"
slack_verification = "QV4W1TaP4StYiypdgGs9K4ea"
sc = SlackClient(slack_token)

count = 0
result = random.randrange(1, 51)

def start():
    temp = []
    global count
    global result

    result = random.randrange(1, 50)
    count = 1

    temp.append("업다운 게임 입니다.")
    temp.append("시작하겠습니다!\n숫자를 입력해주세요.(1~50)")

    return u'\n'.join(temp)

# 크롤링 함수 구현하기
def updown(text):
    temp = []
    global count
    global result

    text = int(text)

    if count == 5:
        if text == result:
            temp.append("정답입니다!") 
        else :
            temp.append("기회를 다썼습니다.")
            temp.append("정답은 %d 였습니다."%result)
            temp.append("시작  or  ㄱㄱ  or  ㄱ 를 입력하여 재시작해주세요")
    else:
        if text < result:
            temp.append("up!")
            temp.append("기회가 " + str(5-count) + "번 남았습니다")
        elif text > result:
            temp.append("down!")
            temp.append("기회가 " + str(5-count) + "번 남았습니다")
        else:
            temp.append("정답입니다!")
        count += 1

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(temp)

def intrange(text):
    for i in range(1,51):
        if i == int(text):
            return True
    return False

# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        print(text)
        if "시작" in text or "ㄱㄱ" in text or "ㄱ" in text:
            keywords = start()
        elif text[13:].isdigit():
            keywords = updown(text[13:])
        else:
            keywords = "흥!"
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

if __name__ == '__main__':
    app.run(debug=True)
    #app.run('0.0.0.0', port=8080) => app.run(debug=True)
