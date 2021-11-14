#! /usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import os
import pathlib
import sys
from logging.handlers import RotatingFileHandler
from id_function_invokers import FunctionInvokers


def create_rotating_log() -> logging.Logger:
    # noinspection PyUnresolvedReferences
    log_file_path: str = '/tmp/rpc_server.log'
    result: logging.Logger = logging.getLogger("RpcServer")
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

FunctionInvokers.initialize(parent_logger=logger, host='0.0.0.0', port=8000, server=True)
FunctionInvokers.start()
sys.exit(0)
