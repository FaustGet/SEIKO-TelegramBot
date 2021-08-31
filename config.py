import telebot
from pymongo import MongoClient
print("Start")

bot = telebot.TeleBot("1817689739:AAF3cf6qVltFHXmAmjoGE0Sea1dLwUkYACE")

client = MongoClient('mongodb://root:example@mirllex.site:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false')
db = client.telebot