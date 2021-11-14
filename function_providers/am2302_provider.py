# -*- coding: utf-8 -*-
# Temperature and humidity for AM2302-rpi functions provider
# Use of old library Adafruit_DHT, see https://github.com/adafruit/Adafruit_Python_DHT
import datetime
import importlib
import logging
import threading
from abc import ABC
from id_function_invokers import FunctionProvider, FunctionProviderService

_PIN_ERROR_MSG: str = 'Pin must be a valid number in range 0 to 31.'
_MODULE: str = 'Adafruit_DHT'
_MOCK_MODULE: str = 'adafruit_dht-mock'
_TRACE: bool = False


class Am2302FunctionProvider(FunctionProvider):

    def __init__(self, parent_logger: logging.Logger):
        super().__init__(parent_logger)

    def setup(self, pin: int) -> float:
        pass

    def humidity(self) -> float:
        pass

    def temperature(self) -> float:
        pass


class __AbstractAm2302FunctionProviderService(ABC, FunctionProviderService):

    def __init__(self, parent_logger: logging.Logger, module_name: str):
        super().__init__(parent_logger)
        parent_logger.debug('Importing: %s' % module_name)
        self.__module = importlib.import_module(module_name)
        self.__read_lock = threading.Lock()
        self.__read_date = -1
        self.__device = None
        self.__pin = None

    def finalize(self) -> None:
        pass

    def exposed_setup(self, pin: int) -> float:
        self.__pin = pin
        self._logger.debug('Using pin: %s', str(self.__pin))
        self.__device = getattr(self.__module, 'AM2302')
        self._logger.debug('Using device: %s', str(self.__device))

    def __read(self, retry: bool=True):
        with self.__read_lock:
            if self.__read_date == -1 or (datetime.datetime.now() - self.__read_date).total_seconds() >= 2:
                self._logger.debug('reading')
                if retry:
                    self.__humidity, self.__temperature = getattr(self.__module, 'read_retry')(self.__device, self.__pin)
                else:
                    self.__humidity, self.__temperature = getattr(self.__module, 'read')(self.__device, self.__pin)
                self.__read_date = datetime.datetime.now()

    def exposed_humidity(self) -> float:
        if _TRACE:
            self._logger.debug('read_humidity')
        self.__read()
        if _TRACE:
            self._logger.debug('humidity: %s', str(self.__humidity))
        if self.__humidity:
            return round(self.__humidity, 2)
        return None

    def exposed_temperature(self) -> float:
        if _TRACE:
            self._logger.debug('read_temperature')
        self.__read()
        if _TRACE:
            self._logger.debug('temperature: %s', str(self.__temperature))
        if self.__temperature:
            return round(self.__temperature, 2)
        return None


class Am2302FunctionProviderServiceMock(__AbstractAm2302FunctionProviderService):

    def __init__(self, parent_logger: logging.Logger):
        super().__init__(parent_logger, _MOCK_MODULE)


class Am2302FunctionProviderService(__AbstractAm2302FunctionProviderService):

    def __init__(self, parent_logger: logging.Logger):
        super().__init__(parent_logger, _MODULE)
