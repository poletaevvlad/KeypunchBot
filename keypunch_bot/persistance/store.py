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
from abc import ABC, abstractmethod
from .chatdata import ChatData


class Store(ABC):
    @abstractmethod
    def load(self, chat_id: int) -> Optional[ChatData]:
        pass

    def load_or_default(self, chat_id: int) -> ChatData:
        data = self.load(chat_id)
        if data is None:
            data = ChatData()
        return data

    @abstractmethod
    def save(self, chat_id: int, data: ChatData):
        pass
