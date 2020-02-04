# -*- coding: utf-8 -*-
#
# Copyright 2017, 2018, 2020 Vladislav Poletaev
#
# This file is part of KeyunchBot.
#
# KeyunchBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# KeypunchBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with KeypunchBot. If not, see <http://www.gnu.org/licenses/>.

from typing import Optional
from pymongo import MongoClient
from .store import Store
from .chatdata import ChatData, Format


class MongoStore(Store):
    def __init__(self, connection_string: str):
        self.mongo = MongoClient(connection_string)
        self._collection = self.mongo.get_default_database().chat_info

    def load(self, chat_id: int) -> Optional[ChatData]:
        doc = self._collection.find_one({"_id": chat_id})
        if doc is None:
            return doc
        return ChatData(
            show_text=bool(doc.get("show_text", True)),
            output_format=Format(doc.get("format", "default")),
            charset=doc.get("charset", "ebcdic880")
        )

    def save(self, chat_id: int, data: ChatData):
        self._collection.update_one({
            "_id": chat_id
        }, {
            "$set": {
                "show_text": data.show_text,
                "format": data.output_format.value,
                "charset": data.charset
            }
        }, {
            "upsert": True
        })
