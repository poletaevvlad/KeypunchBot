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

from pathlib import Path
import pytest
from PIL import Image, ImageChops
from keypunch_bot.rendering import GraphicsPunchcardRenderer, GraphicsStream
from tests.rendering.test_text_renderer import TAPE, CARD


@pytest.mark.parametrize("show_text, image_name", [
    (True, "card_text.png"), (False, "card_no_text.png")
])
def test_punchcard_renderer(show_text, image_name):
    stream = GraphicsStream("png")
    renderer = GraphicsPunchcardRenderer()
    renderer(stream, CARD, show_text)
    result = Image.open(next(stream.generate_files()))

    image_path = Path(__file__).parents[0] / "assets" / image_name
    expected_image = Image.open(str(image_path))

    assert not ImageChops.difference(result, expected_image).getbbox()
