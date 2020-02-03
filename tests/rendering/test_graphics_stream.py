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

from PIL import Image
from keypunch_bot.rendering import GraphicsStream


def create_image(p11, p12, p21, p22):
    image = Image.new("RGBA", (2, 2), color=(255, 255, 255, 0))
    image.putpixel((0, 0), p11)
    image.putpixel((1, 0), p12)
    image.putpixel((0, 1), p21)
    image.putpixel((1, 1), p22)
    return image.resize((50, 50), Image.NEAREST)


def color_equal(color1, color2):
    return all(abs(c1 - c2) < 10 for c1, c2 in zip(color1, color2))


def test_layer_compose():
    image1 = create_image((255, 0, 0, 255), (255, 0, 0, 255),
                          (0, 0, 0, 0), (0, 0, 0, 0))
    image2 = create_image((0, 255, 0, 255), (0, 0, 0, 0),
                          (0, 255, 0, 255), (0, 0, 0, 0))
    image3 = create_image((0, 0, 255, 255), (0, 0, 0, 0),
                          (0, 0, 0, 0), (0, 0, 255, 255))

    stream = GraphicsStream("png")
    stream.add_layer(image1)
    stream.add_layer(image2)
    stream.break_page()
    stream.add_layer(image3)

    results = list(stream.generate_files())
    res1 = Image.open(results[0])
    res2 = Image.open(results[1])

    assert res1.getpixel((10, 10)) == (0, 255, 0, 255)
    assert res1.getpixel((40, 10)) == (255, 0, 0, 255)
    assert res1.getpixel((10, 40)) == (0, 255, 0, 255)
    assert res1.getpixel((40, 40)) == (0, 0, 0, 0)

    assert res2.getpixel((10, 10)) == (0, 0, 255, 255)
    assert res2.getpixel((10, 40)) == (0, 0, 0, 0)
    assert res2.getpixel((40, 10)) == (0, 0, 0, 0)
    assert res2.getpixel((40, 40)) == (0, 0, 255, 255)


def test_jpeg_background():
    image1 = create_image((255, 0, 0, 255), (255, 0, 0, 255),
                          (0, 0, 0, 0), (0, 0, 0, 0))
    image2 = create_image((0, 255, 0, 255), (0, 0, 0, 0),
                          (0, 255, 0, 255), (0, 0, 0, 0))

    stream = GraphicsStream("jpeg")
    stream.add_layer(image1)
    stream.add_layer(image2)
    res = Image.open(next(stream.generate_files()))

    assert color_equal(res.getpixel((10, 10)), (0, 255, 0))
    assert color_equal(res.getpixel((40, 10)), (255, 0, 0))
    assert color_equal(res.getpixel((10, 40)), (0, 255, 0))
    assert color_equal(res.getpixel((40, 40)), (255, 255, 255))
