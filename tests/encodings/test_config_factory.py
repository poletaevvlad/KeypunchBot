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

import itertools
import pytest
from keypunch_bot.encodings import params_factory, EncodingType, EncodingParams
from keypunch_bot.persistance import Format


@pytest.mark.parametrize("encoding_format, encoding_type", itertools.product(
    [Format.DEFAULT, Format.PNG, Format.TEXT],
    [EncodingType.PUNCHCARD, EncodingType.TAPE]
))
def test_factory_types(encoding_format, encoding_type):
    params = params_factory(encoding_format, encoding_type)
    assert isinstance(params, EncodingParams)
    assert isinstance(params.per_page, int)
    assert isinstance(params.max_length, int)
    assert isinstance(params.max_pages, int)
    assert isinstance(params.break_with_line, bool)
