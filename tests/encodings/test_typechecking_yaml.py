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

from typing import Dict, Any
from pathlib import Path
import pytest
import yaml
from keypunch_bot.encodings import EncodingType
from keypunch_bot.encodings.loader import parse_charset


@pytest.fixture(params=[
    "ascii.yaml", "ebcdic.yaml", "ebcdic880.yaml", "ita2.yaml", "mtk2.yaml"
])
def encoding_dict(request) -> Dict[str, Any]:
    path = Path(__file__).parents[2] / "keypunch_bot" / "data" / "charsets"
    with (path / request.param).open() as file:
        return yaml.load(file, yaml.SafeLoader)


def test_loading_typecheck(encoding_dict):
    charset_id, charset = parse_charset(encoding_dict)

    assert isinstance(charset_id, str)
    assert isinstance(charset.name, str)
    assert isinstance(charset.type, EncodingType)
    assert isinstance(charset.substitutions, dict)
    for key, value in charset.substitutions.items():
        assert isinstance(key, str)
        assert isinstance(value, str)

    for char in charset:
        assert isinstance(char, str)
        entry = charset[char]
        assert all(isinstance(x, int) for x in entry.activation)
        assert all(isinstance(x, int) for x in entry.codes)
