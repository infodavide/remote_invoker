# -*- coding: utf-8 -*-
# WiringPi mock
__author__  = "Davide Rolland <david@infodavid.org>"
__status__  = "development"
# The following module attributes are no longer updated.
__version__ = "0.1"
__date__    = "2021/11/29"
from typing import Any, List
from PIL import ImageFont

__fonts_default_font = ImageFont.load_default()

def font(name: str) -> Any:
    return __fonts_default_font

AmaticSCBold: ImageFont = __fonts_default_font
AmaticSCRegular: ImageFont = __fonts_default_font
BitbuntuFull: ImageFont = __fonts_default_font
Bitbuntu: ImageFont = __fonts_default_font
Bitocra13Full: ImageFont = __fonts_default_font
BitocraFull: ImageFont = __fonts_default_font
FredokaOneRegular: ImageFont = __fonts_default_font
PressStart2PRegular: ImageFont = __fonts_default_font
 