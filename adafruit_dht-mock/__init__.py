# -*- coding: utf-8 -*-
# WiringPi mock
__author__  = "Davide Rolland <david@infodavid.org>"
__status__  = "development"
# The following module attributes are no longer updated.
# See https://github.com/adafruit/Adafruit_Python_DHT
__version__ = "0.1"
__date__    = "2021/11/29"
import random

AM2302:str = 'AM2302'
__adafruit_dht_humidity: float = round(random.uniform(0.0, 25.4), 2)
__adafruit_dht_temperature: float = round(random.uniform(-10.5, 39.5), 2)


def read(sensor, pin) -> ():
    return (globals()['__adafruit_dht_humidity'],  globals()['__adafruit_dht_temperature'])

def read_retry(sensor, pin) -> ():
    return (globals()['__adafruit_dht_humidity'],  globals()['__adafruit_dht_temperature'])

def set_humidity(humidity: float) -> None:
    globals()['__adafruit_dht_humidity'] = humidity

def set_temperature(temperature: float) -> None:
    globals()['__adafruit_dht_temperature'] = temperature