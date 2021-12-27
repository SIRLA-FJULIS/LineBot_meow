import os
import random
import pymongo
from flask import Flask, request, abort
from dotenv import load_dotenv

from linebot import (
	LineBotApi, WebhookHandler
)
from linebot.exceptions import (
	InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)
load_dotenv() # 載入.env

line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# mongoDB database
myclient = pymongo.MongoClient('mongodb+srv://user_try:library@cluster0.4ejzf.gcp.mongodb.net/test')
mydb = myclient["meow"] # 指定資料庫
players = mydb["players"] # 指定資料表

cat_toy = {'普通的逗貓棒':['https://i.imgur.com/jtbU0Gi.png'], '一條魚':['https://i.imgur.com/ncK4QZL.png'], '一隻老鼠':['https://i.imgur.com/mb6Ws0g.png', 'https://i.imgur.com/wTJCm9H.png']}
cat_food = {'點心':'https://i.imgur.com/wLs0yHy.png', '罐頭':'https://i.imgur.com/g4iJv1x.png', '貓糧':'https://i.imgur.com/9ZqH3Rk.png'}
Emergencies = ['貓貓趴在你的電腦鍵盤上，偷偷看著你', '貓貓睡著了，請不要吵到他', '貓貓蹲在你背後，她感覺餓了', '貓貓坐在你腳上，蹭了你的肚子']
love = ['https://i.imgur.com/PzuAI3G.png', 'https://i.imgur.com/zOI0H0i.png']

@handler.add(FollowEvent)
def handle_follow(event):
	UserId = event.source.user_id
	profile = line_bot_api.get_profile(UserId)
	player_data = { 
		"PlayerName": profile.display_name,
		"PlayerId": UserId,
		"impression": 0,
	}
	players.insert_one(player_data)

@handler.add(UnfollowEvent)
def handle_unfollow(event):
	# 抓取退出者資料並刪除資料 
	players.delete_one({"PlayerId":event.source.user_id})

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
	# 取得抓取使用者資訊 - line
	UserId = event.source.user_id
	player_information = players.find({ "PlayerId":UserId })


	# 取得使用者資訊 - database
	for i in player_information:
		Impression = i['impression']

	reply = ""

	if event.message.text == "餵食":

		reply = TemplateSendMessage(
			alt_text = 'Buttons template',
			template = ButtonsTemplate(
				thumbnail_image_url='https://i.imgur.com/oMAspmB.png',
				title='餵食',
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

		line_bot_api.reply_message(event.reply_token, reply)

	elif event.message.text == "逗貓":

		reply = TemplateSendMessage(
			alt_text = 'Buttons template',
			template = ButtonsTemplate(
				thumbnail_image_url='https://i.imgur.com/2YHXdZG.png',
				title='逗貓',
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

		line_bot_api.reply_message(event.reply_token, reply)
	elif event.message.text == "查看好感度":
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage(text=str(Impression))
		)
	elif event.message.text in cat_toy:

		add = random.randint(-10,10)
		if add <= 0:
			reply = random.choice(["去去，貓貓不想跟你玩了", "去去，奴才走"])
		else:
			reply = random.choice(["我才沒有想跟你玩呢!(撲過去", "走開，我才沒有要跟你玩呢(偷瞄"])

		players.update_one({ "PlayerId": UserId},{ "$set": { "impression": Impression + add}})

		reply = [
		ImageSendMessage(
			original_content_url=random.choice(cat_toy[event.message.text]),
			preview_image_url=random.choice(cat_toy[event.message.text])
		),
		TextSendMessage(text=reply)
		]

		line_bot_api.reply_message(event.reply_token, reply)
	elif event.message.text in cat_food:

		add = random.randint(-15,30)
		if add <= 0:
			reply = "貓貓覺得難吃"
		else:
			reply = "奴才做得不錯嘛"

		players.update_one({ "PlayerId": UserId},{ "$set": { "impression": Impression + add}})
	
		reply = [
		ImageSendMessage(
			original_content_url=cat_food[event.message.text],
			preview_image_url=cat_food[event.message.text]
		),
		TextSendMessage(text=reply)
		]

		line_bot_api.reply_message(event.reply_token,reply)


	else:
		if  Impression >= 100:
			picture = random.choice(love)
			reply = [
			ImageSendMessage(
			original_content_url=picture,
			preview_image_url=picture
			),
			TextSendMessage(text=reply + meow)
			]

			line_bot_api.reply_message(event.reply_token,reply)
		elif  Impression >= 75:
			if random.randint(0,100) // 5 == 0:
				reply = [
				TextSendMessage(text=random.choice(Emergencies)),
				TextSendMessage(text=reply + meow)
				]
			else:
				reply = TextSendMessage(text=reply + meow)

			line_bot_api.reply_message(event.reply_token,reply)
		else:
			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage(text="喵喵睡著了")
			)
		
if __name__ == "__main__":
	app.run()

# https://cat-for-you.herokuapp.com