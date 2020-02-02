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

from keypunch_bot.encodings import CharacterSet, EncodingType


def test_creating():
    charset = CharacterSet("Charset", EncodingType.PUNCHCARD)
    charset.add_characters(dict(a=[1, 2, 3], b=[4, 6]))
    charset.add_characters(dict(c=[7]), activation=[15])

    assert charset.name == "Charset"
    assert charset.type == EncodingType.PUNCHCARD

    assert charset["a"].codes == [1, 2, 3]
    assert not charset["a"].needs_activation

    assert charset["c"].codes == [7]
    assert charset["c"].needs_activation
    assert charset["c"].activation == [15]


def test_encoding_simple():
    charset = CharacterSet("Charset", EncodingType.PUNCHCARD)
    charset.add_characters(dict(a=[1, 2], b=[3]))

    result = charset.encode("acacb", 3)
    assert result.result == [[("a", 1), ("", 2), ("a", 1)],
                             [("", 2), ("b", 3)]]
    assert result.unknown == {"c"}
    assert result.unknown_count == 2
