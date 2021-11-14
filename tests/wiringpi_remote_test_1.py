#! /usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import os
import pathlib
import time
from logging.handlers import RotatingFileHandler
from id_function_invokers import FunctionInvokers
from function_providers.wiringpi_provider import WiringPiFunctionProvider

PIN_1: int = 0
PIN_2: int = 2
PIN_3: int = 12

def create_rotating_log() -> logging.Logger:
    # noinspection PyUnresolvedReferences
    log_file_path: str = '/tmp/wiringpi_test.log'
    result: logging.Logger = logging.getLogger("WiringPiTest")
    path_obj: pathlib.Path = pathlib.Path(log_file_path)
    if not os.path.exists(path_obj.parent.absolute()):
        os.makedirs(path_obj.parent.absolute())
    if os.path.exists(log_file_path):
        open(log_file_path, 'w').close()
    else:
        path_obj.touch()
    # noinspection Spellchecker
    formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler: logging.Handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    result.addHandler(console_handler)
    file_handler: logging.Handler = RotatingFileHandler(log_file_path, maxBytes=1024 * 1024 * 5, backupCount=5)
    # noinspection PyUnresolvedReferences
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    result.addHandler(file_handler)
    # noinspection PyUnresolvedReferences
    result.setLevel(logging.DEBUG)
    return result


logger: logging.Logger = create_rotating_log()

# FunctionInvokers.initialize(parent_logger=logger, host='127.0.0.1', server=False)
FunctionInvokers.initialize(parent_logger=logger, host='192.168.168.65')
provider: WiringPiFunctionProvider = FunctionInvokers.get_provider(WiringPiFunctionProvider)

logger.info('Setup')
provider.wiringPiSetup()
provider.pinMode(PIN_1, 1)
provider.pinMode(PIN_2, 1)
provider.pinMode(PIN_3, 1)

logger.info('All off')
provider.digitalWrite(PIN_1, 0)
provider.digitalWrite(PIN_2, 0)
provider.digitalWrite(PIN_3, 0)

try:
    while True:
        provider.digitalWrite(PIN_1, 1)
        provider.digitalWrite(PIN_2, 0)
        provider.digitalWrite(PIN_3, 0)
        time.sleep(3)
        provider.digitalWrite(PIN_1, 0)
        provider.digitalWrite(PIN_2, 1)
        provider.digitalWrite(PIN_3, 0)
        time.sleep(0.6)
        provider.digitalWrite(PIN_1, 0)
        provider.digitalWrite(PIN_2, 0)
        provider.digitalWrite(PIN_3, 1)
        time.sleep(3)
        provider.digitalWrite(PIN_1, 0)
        provider.digitalWrite(PIN_2, 1)
        provider.digitalWrite(PIN_3, 0)
        time.sleep(0.6)
finally:
    logger.info('All off')
    provider.digitalWrite(PIN_1, 0)
    provider.digitalWrite(PIN_2, 0)
    provider.digitalWrite(PIN_3, 0)
    logger.info('Setup all as input')
    provider.pinMode(PIN_1, 0)
    provider.pinMode(PIN_2, 0)
    provider.pinMode(PIN_3, 0)
