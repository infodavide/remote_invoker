# -*- coding: utf-8 -*-
# WiringPi mock
__author__  = "Davide Rolland <david@infodavid.org>"
__status__  = "development"
# The following module attributes are no longer updated.
__version__ = "0.1"
__date__    = "2021/11/29"
import pygame
import numpy
from PIL import Image

__lcd_dimensions = (128, 64)
__lcd_scale: int = 3
__lcd_screen = None