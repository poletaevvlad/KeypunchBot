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

from typing import Union
from .bot import ChatBot, MessageContext


# pylint: disable=no-self-use
class KeyPunchBot(ChatBot):
    def initialize(self):
        self.on_command("start", self.show_message("help", "welcome"))
        self.on_command("about", self.show_message("help", "about"))

    def show_message(self, *message_id: Union[str, int]):
        def handler(ctx: MessageContext):
            ctx.answer(ctx.lang.__getitem__(*message_id))
        return handler

    def text(self, ctx: MessageContext):
        pass
