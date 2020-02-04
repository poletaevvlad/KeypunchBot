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

from typing import Tuple, Dict, cast
from ..encodings import EncodingType
from ..persistance import Format
from .stream import Stream
from .renderer import Renderer
from .text_stream import TextStream
from .graphics_stream import GraphicsStream
from .text_renderer import punched_tape_renderer, punched_card_renderer
from .graphics_renderer import GraphicsPunchcardRenderer, GraphicsTapeRenderer


IMAGE_FORMATS: Dict[Format, str] = {
    Format.DEFAULT: "png",
    Format.PNG: "png",
    Format.JPEG: "jpeg"
}


def renderer_factory(output_format: Format,
                     medium_type: EncodingType) -> Tuple[Stream, Renderer]:
    stream: Stream
    renderer: Renderer
    if output_format not in IMAGE_FORMATS:
        stream = TextStream()
        if medium_type == EncodingType.TAPE:
            renderer = punched_tape_renderer
        else:
            renderer = punched_card_renderer
    else:
        stream = GraphicsStream(IMAGE_FORMATS[output_format])
        if medium_type == EncodingType.TAPE:
            renderer = cast(Renderer, GraphicsTapeRenderer())
        else:
            renderer = cast(Renderer, GraphicsPunchcardRenderer())

    return stream, renderer
