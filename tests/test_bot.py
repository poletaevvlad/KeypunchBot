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

from unittest.mock import MagicMock
import pytest
from keypunch_bot.bot import MessageContext
from keypunch_bot.persistance import InMemoryStore, ChatData, Format


@pytest.fixture
def context():
    update = MagicMock()
    update.edited_message = None
    update.message.chat_id = 17
    context = MagicMock()
    translation_manager = MagicMock()
    store = InMemoryStore()
    message_context = MessageContext(update, context, translation_manager,
                                     store)
    return update, translation_manager, store, message_context


def test_get_language(context):
    update, translation_manager, _, message_context = context

    update.message.from_user.language_code = "ru"
    lang = message_context.lang
    assert lang is translation_manager.get.return_value
    translation_manager.get.assert_called_with("ru")


def test_no_language(context):
    update, translation_manager, _, message_context = context

    update.message.from_user.language_code = None
    lang = message_context.lang
    assert lang is translation_manager.default_lang


@pytest.mark.parametrize("kwargs, expected", [
    ({"charset": "mtk2"},
     ChatData(charset="mtk2", output_format=Format.TEXT, show_text=True)),
    ({"show_text": False},
     ChatData(charset="ita2", output_format=Format.TEXT, show_text=False)),
    ({"format": Format.PNG},
     ChatData(charset="ita2", output_format=Format.PNG, show_text=True)),
    ({"charset": "mtk2", "format": Format.PNG, "show_text": False},
     ChatData(charset="mtk2", output_format=Format.PNG, show_text=False))
])
def test_save(context, kwargs, expected):
    _, _, store, message_context = context
    store.save(17, ChatData(charset="ita2", output_format=Format.TEXT))
    message_context.save(**kwargs)

    result = store.load(17)
    assert result == expected


def test_save_no_chage_1(context):
    _, _, store, message_context = context
    message_context.save()
    assert store.load(17) is None


def test_save_no_chage_2(context):
    _, _, store, message_context = context
    message_context.save(charset="ebcdic880", format=Format.DEFAULT,
                         show_text=True)
    assert store.load(17) is None


@pytest.mark.parametrize("message, expected", [
    ("text message", "text message"),
    ("/ text message", "/ text message"),
    ("/command arguments", "arguments"),
    ("/command123 arguments", "arguments"),
    ("/COMMAND_name arguments", "arguments"),
    ("//command arguments", "/command arguments")
])
def test_getting_message(context, message, expected):
    update, _, _, message_context = context
    update.message.text = message
    assert message_context.message == expected
