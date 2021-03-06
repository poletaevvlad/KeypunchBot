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
from keypunch_bot.utils import lazy_property


# pylint: disable=too-few-public-methods
class MockClass:
    def __init__(self):
        self.magic_mock = MagicMock()

    @lazy_property
    def prop(self):
        return self.magic_mock()


def test_access():
    obj = MockClass()

    val1 = obj.prop
    obj.magic_mock.assert_called_once()
    assert val1 is obj.magic_mock.return_value
    obj.magic_mock.reset_mock()

    val2 = obj.prop
    assert val1 is val2
    obj.magic_mock.assert_not_called()
