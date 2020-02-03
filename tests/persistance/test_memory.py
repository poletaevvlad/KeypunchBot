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

from keypunch_bot.persistance import InMemoryStore, ChatData


def test_load_save():
    store = InMemoryStore()
    assert store.load(17) is None

    data = ChatData(show_text=False, charset="ita2")
    store.save(17, data)
    assert store.load(17) == data


def test_default():
    store = InMemoryStore()
    assert store.load_or_default(17) == ChatData()
