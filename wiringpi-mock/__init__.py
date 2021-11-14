# -*- coding: utf-8 -*-
# WiringPi mock
__author__  = "Davide Rolland <david@infodavid.org>"
__status__  = "development"
# The following module attributes are no longer updated.
__version__ = "0.1"
__date__    = "2021/11/29"
from typing import List

ListOfFloats = List[float]
ListOfInt = List[int]

INPUT_MODE: int = 0
OUTPUT_MODE: int = 1
PWM_MODE: int = 2
NO_PULL_DOWN_UP: int = 0
PULL_DOWN: int = 1
PULL_UP: int = 2
PWM_MS: int = 0
PWM_BALANCED: int = 0

__pwm_mode: int = PWM_MS
__pins: ListOfFloats = list()
__io_mode: ListOfInt = list()
__pull_mode: ListOfInt = list()

for i in range(1, 18):
    __pins.append(0)
    __io_mode.append(INPUT_MODE)
    __pull_mode.append(NO_PULL_DOWN_UP)


def __log_pins() -> None:
    print(str(__pins).strip('[]').replace(', ', ''))


def wiringPiSetup() -> None:
    pass


def wiringPiSetupSys() -> None:
    pass


def wiringPiSetupGpio() -> None:
    pass


def pwmSetMode(mode: int) -> None:
    pwm_mode = mode


def pinMode(pin: int, mode: int) -> None:
    __io_mode[pin] = mode


def pullUpDnControl(pin: int, mode: int) -> None:
    __pull_mode[pin] = mode


def digitalWrite(pin: int, value: float) -> None:
    if __io_mode[pin] == OUTPUT_MODE:
        __pins[pin] = value
        __log_pins()


def digitalRead(pin: int) -> float:
    if __io_mode[pin] == INPUT_MODE:
        return __pins[pin]


def pwmWrite(pin: int, value: int) -> None:
    if __io_mode[pin] == PWM_MODE:
        __pins[pin] = value
        __log_pins()
