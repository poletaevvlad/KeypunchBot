# -*- coding: utf-8 -*-

from pymongo import MongoClient
from urllib.parse import quote_plus


class MongoDataManager:
    def __init__(self, server, database, user, password):
        props = dict(user=quote_plus(user), password=quote_plus(password),
                     server=server, database=database)
        url = "mongodb://{user}:{password}@{server}/{database}".format(**props)
        self.client = MongoClient(url)
        self.db = self.client[database]
        self.collection = self.db.chat_info

    def get(self, chat_id):
        data = self.collection.find_one({"_id": chat_id})
        if data is None:
            chat_data = ChatData(chat_id)
        else:
            chat_data = ChatData.from_database(data)
        return chat_data

    def put(self, chat_data):
        if chat_data.in_database:
            doc = dict(show_text=chat_data.show_text, format=chat_data.format)
            self.collection.update_one({"_id": chat_data.id}, {"$set": doc})
        else:
            doc = {"_id": chat_data.id, "show_text": chat_data.show_text,
                   "format": chat_data.format}
            self.collection.insert_one(doc)


class ChatData:
    def __init__(self, id):
        self.in_database = False
        self.id = id
        self.show_text = True
        self.format = None

    @classmethod
    def from_database(cls, data):
        chat_data = ChatData(data["_id"])
        chat_data.show_text = data["show_text"]
        chat_data.format = data["format"]
        chat_data.in_database = True
        return chat_data
