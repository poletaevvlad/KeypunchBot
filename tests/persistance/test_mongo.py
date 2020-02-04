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

from unittest.mock import patch
import pytest
import mongomock
from keypunch_bot.persistance import MongoStore, ChatData, Format

DATA = ChatData(show_text=False, output_format=Format.PNG, charset="ita2")
RECORD = {"_id": 74, "show_text": False, "format": "png", "charset": "ita2"}
RECORD_2 = {"_id": 74, "show_text": True, "format": "text", "charset": "ita2"}


@patch("keypunch_bot.persistance.mongo.MongoClient", mongomock.MongoClient)
def test_inserting():
    store = MongoStore("mongodb://localhost/database")
    store.save(74, DATA)
    collection = store.mongo.database.chat_info
    assert collection.find_one({"_id": 74}) == RECORD


@patch("keypunch_bot.persistance.mongo.MongoClient", mongomock.MongoClient)
def test_updating():
    store = MongoStore("mongodb://localhost/database")
    collection = store.mongo.database.chat_info
    collection.insert_one(RECORD_2)

    store.save(74, DATA)
    assert collection.find_one({"_id": 74}) == RECORD


@patch("keypunch_bot.persistance.mongo.MongoClient", mongomock.MongoClient)
def test_loading():
    store = MongoStore("mongodb://localhost/database")
    collection = store.mongo.database.chat_info
    collection.insert_one(RECORD)
    assert store.load(74) == DATA


@patch("keypunch_bot.persistance.mongo.MongoClient", mongomock.MongoClient)
def test_loading_nothing():
    store = MongoStore("mongodb://localhost/database")
    assert store.load(74) is None
