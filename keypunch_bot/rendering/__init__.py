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

from .stream import Stream  # noqa
from .text_stream import TextStream  # noqa
from .graphics_stream import GraphicsStream  # noqa

from .renderer import Renderer  # noqa
from .text_renderer import punched_tape_renderer  # noqa
from .text_renderer import punched_card_renderer  # noqa
from .graphics_renderer import GraphicsPunchcardRenderer  # noqa
from .graphics_renderer import GraphicsTapeRenderer  # noqa

from .factory import renderer_factory  # noqa
