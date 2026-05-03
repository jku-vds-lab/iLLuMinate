from enum import Enum

class VariationMode(Enum):
    TOPICS = "topic"
    STYLE = "style"
    FORMAT = "format"


def variation_mode_2_label(mode: VariationMode):
    if mode is VariationMode.TOPICS:
        return "Topic"
    elif mode is VariationMode.STYLE:
        return "Style"
    elif mode is VariationMode.FORMAT:
        return "Format"


def variation_mode_2_color(mode: VariationMode):
    if mode is VariationMode.TOPICS:
        return "#31759b"
    elif mode is VariationMode.STYLE:
        return "#ce5c00"
    elif mode is VariationMode.FORMAT:
        return "#7b4884"
