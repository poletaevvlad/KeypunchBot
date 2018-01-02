import webapp2
import yaml
from keypunch_bot import KeyPunchBot
from telegram import Update
import json


class MainPage(webapp2.RequestHandler):

    def get(self):
        config = yaml.load("config.yaml")
        bot = KeyPunchBot(config["api_key"])

        update = Update.de_json(json.loads(self.request.body), bot)
        bot.dispatcher.process_update(update)


app = webapp2.WSGIApplication([('/', MainPage), ], debug=True)
