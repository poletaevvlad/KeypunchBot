# -*- coding: utf-8 -*-

from urllib.parse import quote_plus

from pymongo import MongoClient


class InMemoryDataManager:
    def __init__(self):
        self.data = dict()

    def get(self, chat_id):
        if chat_id in self.data:
            return self.data.get(chat_id)
        else:
            return ChatData(chat_id)

    def put(self, chat_data):
        self.data[chat_data.id] = chat_data


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
        doc = dict(show_text=chat_data.show_text, format=chat_data.format,
                   char_table=chat_data.char_table)
        if chat_data.in_database:
            self.collection.update_one({"_id": chat_data.id}, {"$set": doc})
        else:
            doc["_id"] = chat_data.id
            self.collection.insert_one(doc)


class ChatData:
    __slots__ = ["in_database", "id", "show_text", "format", "char_table"]

    def __init__(self, chat_id):
        self.in_database = False
        self.id = chat_id
        self.show_text = True
        self.format = None
        self.char_table = None

    @classmethod
    def from_database(cls, data):
        chat_data = ChatData(data["_id"])
        chat_data.show_text = data["show_text"]
        chat_data.format = data["format"]
        chat_data.char_table = data["char_table"] if "char_table" in data \
            else None
        chat_data.in_database = True
        return chat_data
