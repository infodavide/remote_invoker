#! /usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import os
import pathlib
import time
from logging.handlers import RotatingFileHandler
from id_function_invokers import FunctionInvokers
from function_providers.am2302_provider import Am2302FunctionProvider

PIN_1: int = 23

def create_rotating_log() -> logging.Logger:
    # noinspection PyUnresolvedReferences
    log_file_path: str = '/tmp/am2302_test.log'
    result: logging.Logger = logging.getLogger("Am2302Test")
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
#FunctionInvokers.initialize(parent_logger=logger, host='127.0.0.1')
FunctionInvokers.initialize(parent_logger=logger, host='192.168.168.65')
provider: Am2302FunctionProvider = FunctionInvokers.get_provider(Am2302FunctionProvider)

provider.setup(PIN_1)

while True:
    logger.info('Temperature: %s', provider.temperature())
    logger.info('Humidity: %s', provider.humidity())
    time.sleep(3)
