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

from unittest.mock import patch, MagicMock
import pytest
from PIL import Image
from keypunch_bot.keypunchbot import KeyPunchBot
from keypunch_bot.persistance import Format, ChatData
from keypunch_bot import __version__ as version


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

    bot.show_about(context)
    context.answer.assert_called_with(context.lang.get.return_value)
    context.lang.get.assert_called_with("help", "about", version=version)



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


def test_generate_images():
    with patch("keypunch_bot.bot.Updater"):
        bot = KeyPunchBot("", MagicMock())

    context = MagicMock()
    bot.generate(context, Format.DEFAULT, "ebcdic", "hello\nworld")
    assert context.send_photo.call_count == 2
    for call in context.send_photo.call_args_list:
        img = Image.open(call[0][0])
        assert img.format == "PNG"


def test_generatign_files():
    with patch("keypunch_bot.bot.Updater"):
        bot = KeyPunchBot("", MagicMock())

    context = MagicMock()
    bot.generate(context, Format.JPEG, "ebcdic", "hello\nworld")
    assert context.send_file.call_count == 2
    for filename, call in zip(["card-1.jpg", "card-2.jpg"],
                              context.send_file.call_args_list):
        img = Image.open(call[0][0])
        assert img.format == "JPEG"
        assert call[0][1] == filename


def test_setting_format_argument():
    with patch("keypunch_bot.bot.Updater"):
        bot = KeyPunchBot("", MagicMock())

    context = MagicMock()
    context.data = ChatData()
    context.message = "hello, world"
    bot.set_format(context, Format.PNG)

    context.send_file.assert_called()
    context.save.assert_not_called()


def test_setting_format_no_argument():
    with patch("keypunch_bot.bot.Updater"):
        bot = KeyPunchBot("", MagicMock())

    context = MagicMock()
    context.message = ""
    bot.set_format(context, Format.PNG)

    context.save.assert_called_with(format=Format.PNG)
    context.send_file.assert_not_called()
    context.answer.assert_called_with(context.lang.get.return_value)
    context.lang.get.assert_called_with("format", "prompt",
                                        format=["format", "png"])


def test_clearing_format_on_text():
    with patch("keypunch_bot.bot.Updater"):
        bot = KeyPunchBot("", MagicMock())

    context = MagicMock()
    context.data = ChatData()
    context.message = "hello, world"
    bot.text(context)
    context.save.assert_called_with(format=Format.DEFAULT)


def test_cancel_nothing():
    with patch("keypunch_bot.bot.Updater"):
        bot = KeyPunchBot("", MagicMock())

    context = MagicMock()
    context.data = ChatData()
    bot.cancel_format(context)
    context.answer.assert_called_with(context.lang.__getitem__.return_value)
    context.lang.__getitem__.assert_called_with(("cancel", "fail"))


def test_cancel_done():
    with patch("keypunch_bot.bot.Updater"):
        bot = KeyPunchBot("", MagicMock())

    context = MagicMock()
    context.data = ChatData(output_format=Format.PNG)
    bot.cancel_format(context)
    context.answer.assert_called_with(context.lang.__getitem__.return_value)
    context.lang.__getitem__.assert_called_with(("cancel", "done"))
    context.save.assert_called_with(format=Format.DEFAULT)
