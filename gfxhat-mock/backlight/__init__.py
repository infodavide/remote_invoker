# -*- coding: utf-8 -*-
# WiringPi mock
__author__  = "Davide Rolland <david@infodavid.org>"
__status__  = "development"
# The following module attributes are no longer updated.
__version__ = "0.1"
__date__    = "2021/11/29"
from typing import Any, List
from .. import __lcd_dimensions

ListOfTuple = List[tuple]
ListOfBool = List[bool]
BacklightPixels = List[ListOfTuple]
__backlight_visible: bool = False
__backlight_pixels: BacklightPixels = list()

for x in range(6):
    __backlight_pixels.append((0, 0, 0))

def set_pixel(x: int, r: int, g: int, b: int) -> None:
    __backlight_pixels[x] = (r, g, b)

def set_all(r: int, g: int, b: int) -> None:
    for x in range(1, len(__backlight_pixels)):
        __backlight_pixels[x] = (r, g, b)

def clear() -> None:
    globals()['__backlight_visible'] = False
    
def show() -> None:
    globals()['__backlight_visible'] = True

def setup() -> None:
    pass
