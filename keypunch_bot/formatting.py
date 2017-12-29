import math
from PIL import Image
import aggdraw


class Formatter:
    num_columns = 80
    
    def __init__(self):
        pass

    def row_numbers(self):
        yield 12
        yield 11
        for i in range(0, 10):
            yield i

    def format(self, codes, text):
        raise Exception("Formatter class cannot be used")


class TextFormatter(Formatter):
    
    def format_line(self, codes_list: list, num: int) -> str:
        return "| " + "".join("x" if i < len(codes_list) and num in codes_list[i] else " " for i in range(80))
    
    def format(self, codes):
        all_codes = list(codes)
        result = ["  " + "_" * 80]
        result += [" /"]
        for line in self.rows_numbers():
            result += [self.format_line(all_codes, line)]
        result += ["|" + "_" * 81]
        return result


class GraphicsFormatter(Formatter):
    dpi = 88
    width = 7.75 * dpi
    height = 3.25 * dpi
    
    padding = 10
    corner_radius = 0.22 * dpi
    corner_cut_width = 0.23 * dpi
    corner_cut_height = 0.42 * dpi
    
    padding_left = int(0.24 * dpi)
    padding_top = int(0.195 * dpi)
    spacing_horizontal = 3
    spacing_vertical = 11
    text_y = -1
    
    column_numbers_y = [dpi * 0.81, dpi * 3.05]
    
    hole_width = 5
    hole_height = 11
    
    def to_px(self, *xy,  half_px=True):
        a = 0.5 if half_px else 0
        return tuple(int(x + self.padding) + a for x in xy)
    
    
class PILFormatter(GraphicsFormatter):
    
    def __init__(self):
        self.text_font = aggdraw.Font("black", "./fonts/Oswald-Regular.ttf", 10)
        self.row_number_font = aggdraw.Font("black", "./fonts/Oswald-Regular.ttf", 10)
        self.col_number_font = aggdraw.Font("black", "./fonts/Oswald-Light.ttf", 7)
    
    def create(self, image_format):
        mode = "RGBA" if image_format == "png" else "RGB"
        color = None if image_format == "png" else (255, 255, 255)
        im = Image.new(mode, (int(self.width + 2 * self.padding), int(self.height + 2 * self.padding)),
            color)
        draw = aggdraw.Draw(im)
        return im, draw
    
    def draw_background(self, draw):
        """ 
        Drawing a background of a punched card.
        This method assumes that corner_cut_width > corner_radius and 
            corner_cut_height > corner_radius"""
        draw.setantialias(False)
        b = aggdraw.Brush("#eeeeee")
        draw.rectangle(self.to_px(0, self.corner_cut_height, self.width, self.height - self.corner_radius), None, b)
        draw.rectangle(self.to_px(self.corner_radius, self.height - self.corner_radius, 
                                  self.width - self.corner_radius, self.height), None, b)
        draw.rectangle(self.to_px(self.corner_cut_width, self.corner_radius, self.width, self.corner_cut_height), None, b)
        draw.rectangle(self.to_px(self.corner_cut_width, 0, self.width - self.corner_radius, self.corner_radius), None, b)
        draw.polygon(self.to_px(self.corner_cut_width, 0, 0, self.corner_cut_height, 
                                self.corner_cut_width, self.corner_cut_height), None, b)
        draw.pieslice(self.to_px(0, self.height - 2 * self.corner_radius, 2 * self.corner_radius, self.height),
                      180, 270, None, b)
        draw.pieslice(self.to_px(self.width - 2 * self.corner_radius, self.height - 2 * self.corner_radius, 
                      self.width, self.height), 270, 0, None, b)
        draw.pieslice(self.to_px(self.width - 2 * self.corner_radius, 0, self.width, 2 * self.corner_radius), 0, 90, 
                      None, b)

    def draw_outline(self, draw):
        draw.setantialias(True)
        p = aggdraw.Pen("black", 1)
        draw.line(self.to_px(self.width - self.corner_radius, 0, self.corner_cut_width, 0, 
                             0, self.corner_cut_height, 0, self.height - self.corner_radius), p)
        draw.arc(self.to_px(0, self.height - 2 * self.corner_radius, 2 * self.corner_radius, self.height),
                 180, 270, p)
        draw.line(self.to_px(self.corner_radius, self.height, self.width - self.corner_radius, self.height), p)
        draw.arc(self.to_px(self.width - 2 * self.corner_radius, self.height - 2 * self.corner_radius, 
                            self.width, self.height), 270, 0, p)
        draw.line(self.to_px(self.width, self.height - self.corner_radius, self.width, self.corner_radius), p)
        draw.arc(self.to_px(self.width - 2 * self.corner_radius, 0, self.width, 2 * self.corner_radius), 0, 90, p)
    
    def draw_text_middle(self, draw, rect, text, font):
        width, height = draw.textsize(text, font)
        draw.text(self.to_px(rect[0] + (rect[2] - rect[0] - width) / 2, 
                             rect[1] + (rect[3] - rect[1] - height) / 2 - 1), text, font)
    
    def draw_numbers(self, draw, codes):
        row_numbers = list(self.row_numbers())
        draw.setantialias(False)
        
        codes_ended = False
        for column in range(self.num_columns):
            if not codes_ended:
                try:
                    indices = next(codes)
                except StopIteration:
                    codes_ended = True
                    
            for row in range(12):
                rect = [self.padding_left + (self.hole_width + self.spacing_horizontal) * column, 
                        self.padding_top + (self.hole_height + self.spacing_vertical) * row]
                rect += [rect[0] + self.hole_width, rect[1] + self.hole_height]
                if not codes_ended and row_numbers[row] in indices:
                    draw.rectangle(self.to_px(rect[0] + 1, rect[1], rect[2] + 1, rect[3], 
                                              half_px=False), aggdraw.Brush("black"))
                elif row >= 2:
                    self.draw_text_middle(draw, rect, str(row - 2), self.row_number_font)
    
    def draw_calumn_numbers(self, draw, y):
        x = self.padding_left
        for i in range(self.num_columns):
            label = str(i + 1)
            width, _ = draw.textsize(label, self.col_number_font)
            draw.text(self.to_px(x + (self.hole_width - width) / 2, y), label, self.col_number_font)
            x += self.hole_width + self.spacing_horizontal
    
    def draw_text(self, draw, text):
        for i, c in enumerate(text):
            x = self.padding_left + i * (self.hole_width + self.spacing_horizontal)
            width, _ = draw.textsize(c, self.text_font)
            draw.text(self.to_px(x + (self.hole_width - width) / 2, self.text_y), c, self.text_font)
    
    def format(self, codes, text, fobj, image_format="png"):
        image, draw = self.create(image_format)
        self.draw_background(draw)
        self.draw_outline(draw)
        self.draw_numbers(draw, codes)
        for column_number_y in self.column_numbers_y:
            self.draw_calumn_numbers(draw, column_number_y)
        if text is not None:
            self.draw_text(draw, text)
        draw.flush()
        del draw
        image.save(fobj, image_format)
