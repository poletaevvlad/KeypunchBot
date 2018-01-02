# -*- coding: utf-8 -*-

true_strings = ["+", "y", "yes", "t", "true", "on"]
false_strings = ["-", "n", "no", "f", "false", "off"]


def parse_boolean(text):
    if text in true_strings:
        return True
    elif text in false_strings:
        return False
    else:
        return None
