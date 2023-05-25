# -*- coding: utf-8 -*-

import logging
from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage
from linebot.models import TextSendMessage
import time
import os

from flask import Flask, request



#################
import openai
	
openai.api_key = os.getenv("OPENAI_API_KEY")
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
#parser = WebhookParser(os.getenv("LINE_CHANNEL_SECRET"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET")) 


	
conversation = []

class ChatGPT:  
    

    def __init__(self):
        
        self.messages = conversation
        self.model = os.getenv("OPENAI_MODEL", default = "gpt-3.5-turbo")
        self.frequency_penalty = 0.0
        self.presence_penalty = 0.0



    def get_response(self, user_input):
        conversation.append({"role": "user", "content": user_input})
        
        start_time = time.time()
        print("record time.")
        try:
            response = openai.ChatCompletion.create(
	            model=self.model,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                messages = self.messages

                )
            conversation.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
        except openai.error.RateLimitError:
            print("open ai rate limit error")
            return "open ai rate limit error"
        print("AI回答內容：")        
        print(response['choices'][0]['message']['content'].strip())
        logging.debug("Response in %.2f seconds: %s" % ((time.time() - start_time), response))
        return response['choices'][0]['message']['content'].strip()
	



chatgpt = ChatGPT()

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
    # Get user's message
    user_message = event.message.text
    
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text="you tell me" + event.message.text)
    # )

    reply_msg = chatgpt.get_response(user_message)
    
    
    print(reply_msg)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_msg)
    )





if __name__ == '__main__':
	    app.run(debug=True, port=os.getenv("PORT", default=5000))
