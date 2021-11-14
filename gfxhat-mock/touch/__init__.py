# -*- coding: utf-8 -*-
# WiringPi mock
__author__  = "Davide Rolland <david@infodavid.org>"
__status__  = "development"
# The following module attributes are no longer updated.
__version__ = "0.1"
__date__    = "2021/11/29"
from typing import Any, List

ListOfBool = List[bool]
ListOfStr = List[str]
ListOfTuple = List[tuple]
BacklightPixels = List[ListOfTuple]

__touch_leds: ListOfBool = list()
__touch_names: ListOfStr = list()
__touch_repeat_rate: int = 0
__touch_repeat_enabled: bool = False
__touch_high_sensitivity_enabled: bool = False
__touch_callbacks = list()

def on(button: int, function: Any) -> None:
    while button >= len(__touch_callbacks):
        __touch_callbacks.append(None)
    __touch_callbacks[button] = function

def setup() -> None:
    pass

def set_led(led: int, state: bool) -> None:
    while led >= len(__touch_leds):
        __touch_leds.append(False)
    __touch_leds[led] = state

def enable_repeat(flag: bool) -> None:
    globals()['__touch_repeat_enabled'] = flag

def get_name(index: int) -> str:
    while index >= len(__touch_names):
        __touch_names.append('')
    return __touch_names[index]

def high_sensitivity() -> None:
    globals()['__touch_high_sensitivity_enabled'] = True

def set_repeat_rate(rate: int) -> None:
    globals()['__touch_repeat_rate'] = rate
