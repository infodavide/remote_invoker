# -*- coding: utf-8 -*-
# WiringPi functions provider
import importlib
import logging
import sys
import traceback
from abc import ABC
from id_function_invokers import FunctionProvider, FunctionProviderService
from typing import List

_PIN_ERROR_MSG: str = 'Pin must be a valid number in range 0 to 31.'
_MODULE: str = 'wiringpi'
_MOCK_MODULE: str = 'wiringpi-mock'
_TRACE: bool = False

ListOfFloats = List[float]


class WiringPiFunctionProvider(FunctionProvider):

    def __init__(self, parent_logger: logging.Logger):
        super().__init__(parent_logger)
        self.__initialized: bool = False

    def wiringPiSetup(self) -> bool:
        pass

    def wiringPiSetupSys(self) -> bool:
        pass

    def wiringPiSetupGpio(self) -> bool:
        pass

    def pinMode(self, pin: int, mode: int) -> bool:
        pass

    def digitalWrite(self, pin: int, value: float) -> bool:
        pass

    def digitalWrites(self, pins_tuple, value: float) -> bool:
        pass

    def digitalRead(self, pin: int) -> float:
        pass

    def digitalReads(self, pins_tuple) -> ListOfFloats:
        pass


class __AbstractWiringPiFunctionProviderMock(ABC, FunctionProviderService):

    def __init__(self, parent_logger: logging.Logger, module_name: str):
        super().__init__(parent_logger)
        parent_logger.debug('Importing: %s' % module_name)
        self.__module = importlib.import_module(module_name)
        self.__initialized: bool = False

    def finalize(self) -> None:
        self._logger.debug('Finalizing...')
        if self.__initialized:
            try:
                for pin in range(0, 31):
                    self.exposed_digitalWrite(pin, 0)
                    self.exposed_pinMode(pin, 0)
            except Exception as ex:
                _, _, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
                self._logger.error(ex)

    def exposed_wiringPiSetup(self) -> bool:
        self._logger.debug('wiringPiSetup')
        self.__initialized: bool = True
        getattr(self.__module, 'wiringPiSetup')()
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_wiringPiSetupSys(self) -> bool:
        self._logger.debug('wiringPiSetupSys')
        self.__initialized: bool = True
        getattr(self.__module, 'wiringPiSetupSys')()
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_wiringPiSetupGpio(self) -> bool:
        self._logger.debug('wiringPiSetupGpio')
        self.__initialized: bool = True
        getattr(self.__module, 'wiringPiSetupGpio')()
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_pinMode(self, pin: int, mode: int) -> bool:
        self._logger.debug('pinMode for pin: %s and mode: %s', str(pin), str(mode))
        if pin is None or int(pin) < 0 or int(pin) > 31:
            raise ValueError(_PIN_ERROR_MSG)
        getattr(self.__module, 'pinMode')(pin, mode)
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_digitalWrite(self, pin: int, value: float) -> bool:
        if _TRACE:
            self._logger.debug('digitalWrite for pin: %s and value: %s', str(pin), str(value))
        if pin is None or int(pin) < 0 or int(pin) > 31:
            raise ValueError(_PIN_ERROR_MSG)
        getattr(self.__module, 'digitalWrite')(pin, value)
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_digitalWrites(self, pins_tuple, value: float) -> bool:
        self._logger.debug('digitalWrites: %s for pins: %s', value, str(len(pins_tuple)))
        f = getattr(self.__module, 'digitalWrite')
        for pin in pins_tuple:
            if pin is None or int(pin) < 0 or int(pin) > 31:
                raise ValueError(_PIN_ERROR_MSG)
            f(pin, value)
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_digitalRead(self, pin: int) -> float:
        if _TRACE:
            self._logger.debug('digitalRead for pin: %s', str(pin))
        if pin is None or int(pin) < 0 or int(pin) > 31:
            raise ValueError(_PIN_ERROR_MSG)
        result = getattr(self.__module, 'digitalRead')(pin)
        if _TRACE:
            self._logger.debug(result)
        return result

    def exposed_digitalReads(self, pins_tuple) -> ListOfFloats:
        self._logger.debug('digitalReads pins: %s', str(len(pins_tuple)))
        r: ListOfFloats = list()
        f = getattr(self.__module, 'digitalRead')
        for pin in pins_tuple:
            if pin is None or int(pin) < 0 or int(pin) > 31:
                raise ValueError(_PIN_ERROR_MSG)
            r.append(f(pin))
        return r


class WiringPiFunctionProviderServiceMock(__AbstractWiringPiFunctionProviderMock):

    def __init__(self, parent_logger: logging.Logger):
        super().__init__(parent_logger, _MOCK_MODULE)


class WiringPiFunctionProviderService(__AbstractWiringPiFunctionProviderMock):

    def __init__(self, parent_logger: logging.Logger):
        super().__init__(parent_logger, _MODULE)
