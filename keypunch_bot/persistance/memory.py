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

from typing import Dict, Optional
from .store import Store
from .chatdata import ChatData


class InMemoryStore(Store):
    def __init__(self):
        self._records: Dict[int, ChatData] = {}

    def load(self, chat_id: int) -> Optional[ChatData]:
        return self._records.get(chat_id, None)

    def save(self, chat_id: int, data: ChatData):
        self._records[chat_id] = data
