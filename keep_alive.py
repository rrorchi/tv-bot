from flask import Flask
from threading import Thread

bot_urls = ['https://tv-bot.murchi-o.repl.co/', ]
timeout = 20 

app = Flask('app')
@app.route('/')
def run():
  app.run(host='0.0.0.0', port=8080)

def keep_alive():
  t = Thread(target=run)
  t.start()