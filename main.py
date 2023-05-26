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
HUGGING_API_KEY = os.getenv("HUGGING_API_KEY")


class Bard:  
    def __init__(self):
        self.headers = { 'Authorization': 'Bearer ' + bard_api_key, 'Content-Type': 'text/plain' }
        self.prompt = "Your name is wilsonGPT, you made by wilson. Please answer the question in the same language and as short as possible. Don't repeat what I said."
        data = { "input": self.prompt}
        req = requests.post('https://api.bardapi.dev/chat', headers=self.headers, json=data)
        try:
            print("prompt:" + req.json()['output'])
        except KeyError:
            print("free trial end error.")

    def get_response(self, user_input):
        data = { "input": user_input}
        req = requests.post('https://api.bardapi.dev/chat', headers=self.headers, json=data)
        try:
            print("answer:" + req.json()['output'])
            return req.json()['output']
        except KeyError:
            print(req)
            return "free trial end error."

pastuserimputs = []
generatedresponses = []

class Hugging:  
    def __init__(self):
        self.API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        self.prompt = "Your name is wilsonGPT, you made by wilson. Please answer the question in the same language and as short as possible. Don't repeat what I said."
        self.response = "Ok, what is your question?"
        self.headers = {"Authorization": "Bearer " + HUGGING_API_KEY}
        # pastuserimputs.append(self.prompt)
        # generatedresponses.append(self.response)

    def query(self, payload):
        response = requests.post(self.API_URL, headers=self.headers, json=payload)
        return response.json()

    def get_response(self, user_input):
        output = self.query({
            "inputs": {
                "past_user_inputs": [self.prompt],
                "generated_responses": [self.response],
                "text": user_input
            },
        })
        try:
            # pastuserimputs = output['past_user_inputs']
            # generatedresponses = output['generated_responses']
            print("Hugging:")
            print(output['generated_text'])
            return output['generated_text']
        except KeyError:
            print(output)
            return "free trial end error."

conversation = []

class ChatGPT:  
    def __init__(self):
        self.messages = conversation
        self.frequency_penalty = 0
        self.presence_penalty = 6
        self.prompt = "Your name is wilsonGPT, you made by wilson. Please answer the question in the same language and as short as possible. Don't repeat what I said."
        self.model = os.getenv("OPENAI_MODEL", default = "gpt-3.5-turbo")
        conversation.append({"role": "user", "content": self.prompt})
        print("self.prompt：")
        try:
            response = openai.ChatCompletion.create(
	            model=self.model,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                messages = self.messages

                )
            conversation.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
            print(response['choices'][0]['message']['content'].strip())
        except openai.error.RateLimitError:
            # print(response)
            print("free trial end error.")  



    def get_response(self, user_input):
        conversation.append({"role": "user", "content": user_input})
        try:
            response = openai.ChatCompletion.create(
	            model=self.model,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                messages = self.messages

                )
            conversation.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
        except openai.error.RateLimitError:
            print("free trial end error.")
            return "free trial end error."
        print("AI回答內容：")        
        print(response['choices'][0]['message']['content'].strip())
        return response['choices'][0]['message']['content'].strip()

class GPT2:  
    def __init__(self):
        self.API_URL = "https://api-inference.huggingface.co/models/gpt2"
        self.prompt = "Your name is wilsonGPT, you made by wilson. Please answer the question in the same language and as short as possible. Don't repeat what I said."
        self.headers = {"Authorization": "Bearer " + HUGGING_API_KEY}

    def query(self, payload):
        response = requests.post(self.API_URL, headers=self.headers, json=payload)
        return response.json()

    def get_response(self, user_input):
        output = self.query({
                    "inputs": self.prompt + "here is the question." + user_input,
                })
        try:
            print("gpt2:")
            print(output['generated_text'])
            return output['generated_text']
        except KeyError:
            print(output)
            return "free trial end error."

bard = Bard()
chatgpt = ChatGPT()
hugging = Hugging()
gpt2 = GPT2()

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

    if(user_message.startswith("tobard:")):
        user_message = user_message.replace("tobard:","")
        print(user_message)
        if(user_message.startswith("test")):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Get your bard message.")
            )
        else:
            reply_msg = bard.get_response(user_message)
            if(reply_msg.find("I don't know what to say.")<0):
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply_msg)
                )

    if(user_message.startswith("togpt:")):
        user_message = user_message.replace("togpt:","")
        print(user_message)
        if(user_message.startswith("test")):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Get your gpt message.")
            )
        else:
            reply_msg = chatgpt.get_response(user_message)
            if(reply_msg.find("I don't know what to say.")<0):
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_msg)
                )

    if(user_message.startswith("togpt2:")):
        user_message = user_message.replace("togpt2:","")
        print(user_message)
        if(user_message.startswith("test")):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Get your gpt2 message.")
            )
        else:
            reply_msg = gpt2.get_response(user_message)
            if(reply_msg.find("I don't know what to say.")<0):
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_msg)
                )

    if(user_message.startswith("tohug:")):
        user_message = user_message.replace("tohug:","")
        print(user_message)
        if(user_message.startswith("test")):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Get your hug message.")
            )
        else:
            reply_msg = hugging.get_response(user_message)
            if(reply_msg.find("I don't know what to say.")<0):
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_msg)
                )

if __name__ == '__main__':
	    app.run(debug=True, port=os.getenv("PORT", default=5000))
