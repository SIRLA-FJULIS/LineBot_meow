import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

Favorability = {}

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    reply = ""
    meow = len(event.message.text) * "喵"
    if event.message.text == "餵食":
        reply = "謝謝您的餵食"
        if event.source.user_id not in Favorability:
            Favorability[event.source.user_id] = 0
        else:
            Favorability[event.source.user_id] = Favorability[event.source.user_id] + 5
        print(Favorability)
    elif event.message.text == "逗貓":
        pass
    elif event.message.text == "查看好感度":
        reply = Favorability[event.source.user_id]

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply + meow)
    )
        
if __name__ == "__main__":
    app.run()

# https://cat-for-you.herokuapp.com 