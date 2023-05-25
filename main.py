# -*- coding: utf-8 -*-

import logging
from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage
from linebot.models import TextSendMessage
import time
import os

import requests

from flask import Flask, request

#################
import openai
	
openai.api_key = os.getenv("OPENAI_API_KEY")
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
#parser = WebhookParser(os.getenv("LINE_CHANNEL_SECRET"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET")) 
bard_api_key = os.getenv("BARD_API_KEY")



class Bearer:  
    

    def __init__(self):
        self.headers = { 'Authorization': 'Bearer ' + bard_api_key, 'Content-Type': 'text/plain' }
        self.prompt = "Your name is wilsonGPT, you made by wilson. Please answer the question in the same language and as short as possible. Don't repeat what I said."
        self.reply_flag = True



    def get_response(self, user_input):
        data = { "input": self.prompt}
        req = requests.post('https://api.bardapi.dev/chat', headers=self.headers, json=data)
        print(req.json())
        data = { "input": user_input}
        req = requests.post('https://api.bardapi.dev/chat', headers=self.headers, json=data)
        print(req.json())
        try:
            return req.json()['output']
        except KeyError:
            return "I don't know what to say."

answer = Bearer()

app = Flask(__name__)
#run_with_ngrok(app)   #starts ngrok when the app is run

@app.route("/")
def hello():
	return "Hello World from Flask in a uWSGI Nginx Docker container with \
	     Python 3.8 (from the example template)"
         
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
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # Get user's messagea

    user_message = event.message.text
    # if(user_message.find("stop")>0):
    #     answer.reply_flag = False
    # elif(user_message.find("start")>0):
    #     answer.reply_flag = True
    # if(answer.reply_flag):
    #     reply_msg = answer.get_response(user_message)
    #     print(reply_msg)
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=reply_msg)
    #     )

    reply_msg = answer.get_response(user_message)
    print(reply_msg)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_msg)
    )





if __name__ == '__main__':
	    app.run(debug=True, port=os.getenv("PORT", default=5000))
