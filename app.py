import os
import random
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction, MessageTemplateAction, URITemplateAction, ImageSendMessage
)

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

Favorability = {}
cat_toy = {'普通的逗貓棒':'https://i.imgur.com/jtbU0Gi.png', '一條魚':'https://i.imgur.com/ncK4QZL.png', '一隻老鼠':'https://i.imgur.com/QKxHgMj.png'}
cat_food = {'點心':'https://i.imgur.com/wLs0yHy.png', '罐頭':'https://i.imgur.com/g4iJv1x.png', '貓糧':'https://i.imgur.com/9ZqH3Rk.png'}
Emergencies = ['貓貓趴在你的電腦鍵盤上，偷偷看著你', '貓貓睡著了，請不要吵到他']
love = {'100':'https://i.imgur.com/zOI0H0i.png'}

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

    cat_talk = ""
    meow = len(event.message.text) * "喵"
    if event.message.text == "餵食":
        add = random.randint(-10,30)

        reply = TemplateSendMessage(
            alt_text = 'Buttons template',
            template = ButtonsTemplate(
                thumbnail_image_url='https://i.imgur.com/oMAspmB.png',
                title='Menu',
                text='請選擇要餵的食物',
                actions=[
                    MessageTemplateAction(
                        label='點心',
                        text='點心'
                    ),
                    MessageTemplateAction(
                        label='罐頭',
                        text='罐頭'
                    ),
                    MessageTemplateAction(
                        label='貓糧',
                        text='貓糧'
                    )
                ]
            )
        )
        if add <= 0:
            cat_talk = "貓貓覺得難吃"
        else:
            cat_talk = "奴才做得不錯嘛"

        if event.source.user_id not in Favorability:
            Favorability[event.source.user_id] = add
        else:
            Favorability[event.source.user_id] = Favorability[event.source.user_id] + add
        print(Favorability)

    elif event.message.text == "逗貓":

        add = random.randint(-10,10)
        if add <= 0:
            cat_talk = "去去，貓貓不想跟你玩了"
        else:
            cat_talk = random.choice(["我才沒有想跟你玩呢!(撲過去", "走開，我才沒有要跟你玩呢(偷喵"])

        if event.source.user_id not in Favorability:
            Favorability[event.source.user_id] = add
        else:
            Favorability[event.source.user_id] = Favorability[event.source.user_id] + add

        reply = TemplateSendMessage(
            alt_text = 'Buttons template',
            template = ButtonsTemplate(
                thumbnail_image_url='https://i.imgur.com/2YHXdZG.png',
                title='Menu',
                text='請選擇一根逗貓棒',
                actions=[
                    MessageTemplateAction(
                        label='普通的逗貓棒',
                        text='普通的逗貓棒'
                    ),
                    MessageTemplateAction(
                        label='一條魚',
                        text='一條魚'
                    ),
                    MessageTemplateAction(
                        label='一隻老鼠',
                        text='一隻老鼠'
                    )
                ]
            )
        )
    elif event.message.text == "查看好感度":
        if event.source.user_id not in Favorability:
            Favorability[event.source.user_id] = 0
        cat_talk = str(Favorability[event.source.user_id])


    if event.message.text == "逗貓":
        line_bot_api.reply_message(event.reply_token, reply)
    elif event.message.text in cat_toy:

        reply = ImageSendMessage(
            original_content_url=cat_toy[event.message.text],
            preview_image_url=cat_toy[event.message.text]
        )

        line_bot_api.reply_message(event.reply_token, reply)

    elif event.message.text == "餵食":
        line_bot_api.reply_message(event.reply_token, reply)
    elif event.message.text in cat_food:

        reply = ImageSendMessage(
            original_content_url=cat_food[event.message.text],
            preview_image_url=cat_food[event.message.text]
        )

        line_bot_api.reply_message(event.reply_token,reply)


    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=cat_talk + meow)
        )
        
if __name__ == "__main__":
    app.run()

# https://cat-for-you.herokuapp.com 