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

from typing import List
from .bot import ChatBot, MessageContext


# pylint: disable=no-self-use
class KeyPunchBot(ChatBot):
    def initialize(self):
        self.on_command("start", self.show_message, ["help", "welcome"])
        self.on_command("about", self.show_message, ["help", "about"])
        self.on_command("showtext", self.set_text_visible, True)
        self.on_command("hidetext", self.set_text_visible, False)

    def show_message(self, ctx: MessageContext, message: List[str]):
        ctx.answer(ctx.lang[message])

    def set_text_visible(self, ctx: MessageContext, visible: bool):
        message_block = "on" if visible else "off"
        if ctx.data.show_text == visible:
            ctx.answer(ctx.lang["text", message_block, "already"])
            return
        ctx.save(show_text=visible)
        ctx.answer(ctx.lang["text", message_block, "set"])

    def text(self, ctx: MessageContext):
        pass
