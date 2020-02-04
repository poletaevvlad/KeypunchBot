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

import pytest
from keypunch_bot.rendering import renderer_factory, punched_card_renderer, \
    punched_tape_renderer, TextStream, GraphicsStream, \
    GraphicsPunchcardRenderer, GraphicsTapeRenderer
from keypunch_bot.encodings import EncodingType
from keypunch_bot.persistance import Format


@pytest.mark.parametrize("medium, expected_renderer", [
    (EncodingType.PUNCHCARD, punched_card_renderer),
    (EncodingType.TAPE, punched_tape_renderer)
])
def test_text_rendering(medium: EncodingType, expected_renderer):
    stream, renderer = renderer_factory(Format.TEXT, medium)
    assert isinstance(stream, TextStream)
    assert renderer is expected_renderer


@pytest.mark.parametrize("medium, renderer_type", [
    (EncodingType.PUNCHCARD, GraphicsPunchcardRenderer),
    (EncodingType.TAPE, GraphicsTapeRenderer)
])
def test_graphics_rendering(medium: EncodingType, renderer_type):
    stream, renderer = renderer_factory(Format.PNG, medium)
    assert isinstance(stream, GraphicsStream)
    assert isinstance(renderer, renderer_type)


@pytest.mark.parametrize("output_format, expected_format", [
    (Format.PNG, "PNG"),
    (Format.JPEG, "JPEG")
])
def test_format(output_format: Format, expected_format: str):
    stream, _renderer = renderer_factory(output_format, EncodingType.PUNCHCARD)
    assert isinstance(stream, GraphicsStream)
    assert stream.output_format == expected_format
