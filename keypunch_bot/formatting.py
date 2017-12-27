import math
import cairo


class Formatter:
    def __init__(self):
        pass

    def rows_numbers(self):
        yield 12
        yield 11
        for i in range(0, 10):
            yield i

    def format(self, codes):
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


class ImageFormatter(Formatter):
    width = 7.75
    height = 3.25
    dpi = 96
    padding = 10
    corner_radius = 0.22
    
    def draw_border(self, ctx):
        ctx.move_to(0.23, 0)
        ctx.line_to(0, 0.42)
        ctx.line_to(0, self.height - self.corner_radius)
        ctx.arc_negative(self.corner_radius, self.height - self.corner_radius, self.corner_radius, math.pi, math.pi / 2)
        ctx.line_to(self.width - self.corner_radius, self.height)
        ctx.arc_negative(self.width - self.corner_radius, self.height - self.corner_radius, self.corner_radius, math.pi / 2, 0)
        ctx.line_to(self.width, self.corner_radius)
        ctx.arc_negative(self.width - self.corner_radius, self.corner_radius, self.corner_radius, 0, -math.pi / 2)
        ctx.close_path()
        
        ctx.stroke_preserve()
        ctx.set_source_rgb (0.9, 0.9, 0.9)
        ctx.fill()
    
    def format(self, codes):
        surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, int(self.width * self.dpi + 2 * self.padding), 
                                      int(self.height * self.dpi + 2 * self.padding))
        ctx = cairo.Context (surface)

       ctx.set_source_rgb (1, 1, 1)
       ctx.rectangle (0, 0, self.width * self.dpi + 2 * self.padding, self.height * self.dpi + 2 * self.padding)
       ctx.fill ()

        ctx.scale(self.dpi, self.dpi)
        ctx.translate((self.padding + 0.5) / self.dpi, (self.padding + 0.5) / self.dpi)

        ctx.set_source_rgb (0, 0, 0)
        ctx.set_line_width (1 / self.dpi)

        self.draw_border(ctx)

        ctx.set_font_size(0.1)
        current_symbol = set()
        rows = list(self.rows_numbers())
        for column in range(80):
            if current_symbol is not None:
                try:
                    current_symbol = next(codes)
                except StopIteration:
                    current_symbol = None
                
            for row in range(12):
                if current_symbol is not None and rows[row] in current_symbol:
                    ctx.set_source_rgb (0, 0, 0)
                    ctx.rectangle (0.238 + 0.0909 * column, 0.31 + 0.25 * row, 0.06, -0.12)
                    ctx.fill ()
                else:
                    ctx.move_to(0.238 + 0.0909 * column, 0.29 + 0.25 * row)
                    ctx.show_text(" " if row < 2 else str(row - 2))

        ctx.set_font_size(0.071)
        for y in [0.911, 3.13]:
            for column in range(80):
                ctx.move_to(0.238 + 0.0909 * column, y)
                ctx.show_text(str(column + 1))
        return surface
