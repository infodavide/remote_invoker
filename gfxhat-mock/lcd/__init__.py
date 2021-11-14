# -*- coding: utf-8 -*-
# WiringPi mock
__author__  = "Davide Rolland <david@infodavid.org>"
__status__  = "development"
# The following module attributes are no longer updated.
__version__ = "0.1"
__date__    = "2021/11/29"
import pygame
from typing import Any, List
from .. import __lcd_dimensions, __lcd_screen, __lcd_scale

ListOfBool = List[bool]
Pixels = List[ListOfBool]
__lcd_visible: bool = False
__lcd_pixels: Pixels = list()

for x in range(__lcd_dimensions[0]):
    l: ListOfBool = list()
    for y in range(__lcd_dimensions[1]):
        l.append(False)
    __lcd_pixels.append(l)

def dimensions() -> ():
    return __lcd_dimensions

def clear() -> None:
    print('LCD clear')
    globals()['__lcd_visible'] = False

def init_screen() -> Any:
    if globals()['__lcd_screen'] is None:
        pygame.init()
        screen = pygame.display.set_mode((__lcd_dimensions[0] * __lcd_scale, __lcd_dimensions[1] * __lcd_scale))
        globals()['__lcd_screen'] = screen
        pygame.display.set_caption('LCD')
        pygame.font.SysFont('monospace', 16)
        screen.fill((0 , 0, 0))
    return globals()['__lcd_screen']

def show() -> None:
    globals()['__lcd_visible'] = True
    init_screen()
    pygame.display.flip()

def set_pixel(x: int, y: int, state: bool) -> None:
    __lcd_pixels[x][y] = state
    screen = init_screen()
    if state:
        for i in range(x * __lcd_scale, x * __lcd_scale + __lcd_scale):
            for j in range(y * __lcd_scale, y * __lcd_scale + __lcd_scale):
                screen.set_at((i, j), (255, 255, 255))
    else:
        for i in range(x * __lcd_scale, x * __lcd_scale + __lcd_scale):
            for j in range(y * __lcd_scale, y * __lcd_scale + __lcd_scale):
                screen.set_at((i, j), (0, 0, 0))
