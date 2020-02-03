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

from unittest.mock import MagicMock, patch
import pytest
from keypunch_bot.bot import MessageContext
from keypunch_bot.keypunchbot import KeyPunchBot
from keypunch_bot.persistance import InMemoryStore, ChatData, Format


@pytest.fixture
def context():
    update = MagicMock()
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
    message_context.save(charset="mtk2", format=Format.PNG, show_text=True)
    assert store.load(17) is None


@pytest.mark.parametrize("current_show, set_show, message, should_update", [
    (True, True, "text.on.already", False),
    (True, False, "text.off.set", True),
    (False, True, "text.on.set", True),
    (False, False, "text.off.already", False),
])
def test_change_show_text(current_show: bool, set_show: bool, message: str,
                          should_update: bool):
    with patch("keypunch_bot.bot.Updater"):
        bot = KeyPunchBot("", MagicMock())
    context = MagicMock()
    context.data.show_text = current_show
    context.lang.__getitem__.side_effect = lambda x: '.'.join(x)

    bot.set_text_visible(context, set_show)
    context.answer.assert_called_with(message)
    if should_update:
        context.save.assert_called_with(show_text=set_show)
    else:
        context.save.assert_not_called()


def test_set_charset_already():
    with patch("keypunch_bot.bot.Updater"):
        bot = KeyPunchBot("", MagicMock())
    context = MagicMock()
    context.data.charset = "mtk2"

    bot.select_character_set(context, "mtk2")
    context.answer.assert_called_with(context.lang.get.return_value)
    context.save.assert_not_called()
    context.lang.get.assert_called_with("set_charset", "already",
                                        encoding="MTK-2")

def test_set_charset_switch():
    with patch("keypunch_bot.bot.Updater"):
        bot = KeyPunchBot("", MagicMock())
    context = MagicMock()
    context.data.charset = "mtk2"

    bot.select_character_set(context, "ascii")
    context.answer.assert_called_with(context.lang.get.return_value)
    context.save.assert_called_with(charset="ascii")
    context.lang.get.assert_called_with("set_charset", "selected",
                                        encoding="ASCII",
                                        kind=["set_charset", "punchcard"])


def test_generate_message_too_many_pages():
    with patch("keypunch_bot.bot.Updater"):
        bot = KeyPunchBot("", MagicMock())

    context = MagicMock()
    bot.generate(context, Format.DEFAULT, "ebcdic", "hello\n" * 7)
    context.answer.assert_called_with(context.lang.get.return_value)
    context.lang.get.assert_called_with("encoding", "too_many_pages",
                                        pages="5")


def test_generate_message_too_long():
    with patch("keypunch_bot.bot.Updater"):
        bot = KeyPunchBot("", MagicMock())

    context = MagicMock()
    bot.generate(context, Format.TEXT, "ita2", "hello" * 1000)
    context.answer.assert_called_with(context.lang.get.return_value)
    context.lang.get.assert_called_with("encoding", "too_long",
                                        columns="1024")


def test_generate_most_unsupported():
    with patch("keypunch_bot.bot.Updater"):
        bot = KeyPunchBot("", MagicMock())

    context = MagicMock()
    bot.generate(context, Format.DEFAULT, "ita2", "привет")
    context.answer.assert_called_with(context.lang.__getitem__.return_value)
    context.lang.__getitem__.assert_called_with(
        ("encoding", "most_unsupported")
    )


def test_generate_some_unsupported():
    with patch("keypunch_bot.bot.Updater"):
        bot = KeyPunchBot("", MagicMock())

    context = MagicMock()
    bot.generate(context, Format.DEFAULT, "ita2", "пhello")
    context.answer.assert_called_with(context.lang.__getitem__.return_value)
    context.lang.__getitem__.assert_called_with(
        ("encoding", "some_unsupported")
    )
