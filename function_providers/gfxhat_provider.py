# -*- coding: utf-8 -*-
# GFX Hat by Pimoroni functions provider
import importlib
import logging
import rpyc
import sys
import traceback
from abc import ABC
from typing import Any
from id_function_invokers import FunctionProvider, FunctionProviderService

_PIN_ERROR_MSG: str = 'Pin must be a valid GPIO number in range 0 to 31.'
_PIXEL_ERROR_MSG: str = 'Pixel must be a valid number in range 0 to 5.'
_COLOR_ERROR_MSG: str = 'Color must be a valid number in range 0 to 255.'
_RATE_ERROR_MSG: str = 'Rate must be a valid number in range 35 to 560.'
_CALLBACK_ERROR_MSG: str = "Function callback must be a valid string with the global function name or <module name> and function name separated by '.'"
_CALLBACK_NOT_FOUND_MSG: str = "Function callback not found: %s"
_MODULE: str = 'gfxhat'
_MOCK_MODULE: str = 'gfxhat-mock'
_LCD: str = '.lcd'
_BACKLIGHT: str = '.backlight'
_TOUCH: str = '.touch'
_FONTS: str = '.fonts'
_TRACE: bool = False


class GfxHatFunctionProvider(FunctionProvider):

    def __init__(self, parent_logger: logging.Logger):
        super().__init__(parent_logger)

    def lcd_font(self, name: str) -> Any:
        pass

    def lcd_dimensions(self) -> ():
        pass

    def lcd_clear(self) -> bool:
        pass

    def lcd_show(self) -> bool:
        pass

    def lcd_set_pixel(self, x: int, y: int, state: bool) -> bool:
        pass

    def lcd_set_pixels(self, x_tuple, y_tuple, state: bool) -> bool:
        pass
    
    def exposed_backlight_clear(self) -> bool:
        pass

    def backlight_set_pixel(self, x: int, r: int, g: int, b: int) -> bool:
        pass

    def backlight_set_pixels(self, x_tuple, r: int, g: int, b: int) -> bool:
        pass

    def backlight_set_all(self, r: int, g: int, b: int) -> bool:
        pass

    def backlight_show(self) -> bool:
        pass

    def backlight_setup(self) -> bool:
        pass

    def touch_on(self, button: int, function: Any) -> bool:
        pass

    def touch_setup(self) -> bool:
        pass

    def touch_set_led(self, led: int, state: bool) -> bool:
        pass

    def touch_set_leds(self, led_tuple, state: bool) -> bool:
        pass

    def touch_enable_repeat(self, flag: bool) -> bool:
        pass

    def touch_get_name(self, index: int) -> str:
        pass

    def touch_high_sensitivity(self) -> bool:
        pass

    def touch_set_repeat_rate(self, rate: int) -> bool:
        pass


class __AbstractGfxHatFunctionProviderService(ABC, FunctionProviderService):

    def __init__(self, parent_logger: logging.Logger, module_name: str):
        super().__init__(parent_logger)
        parent_logger.debug('Importing: %s' % module_name)
        self.__module = importlib.import_module(module_name)
        self.__lcd_module = importlib.import_module(module_name + _LCD)
        self.__backlight_module = importlib.import_module(module_name + _BACKLIGHT)
        self.__touch_module = importlib.import_module(module_name + _TOUCH)
        self.__font_module = importlib.import_module(module_name + _FONTS)
        self.__lcd_cleared: bool = True
        self.__backlight_cleared: bool = True

    def finalize(self) -> None:
        try:
            for x in range(6):
                self.exposed_touch_on(x, None)
                self.exposed_touch_set_led(x, False)
        except Exception as ex:
            _, _, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
            self._logger.error(ex)
        if not self.__backlight_cleared:
            try:
                self.exposed_backlight_clear()
                self.exposed_backlight_show()
            except Exception as ex:
                _, _, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
                self._logger.error(ex)
        if not self.__lcd_cleared:
            try:
                self.exposed_lcd_clear()
                self.exposed_lcd_show()
            except Exception as ex:
                _, _, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
                self._logger.error(ex)

    def exposed_lcd_font(self, name: str) -> Any:
        self._logger.debug('lcd_font using name: %s', name)
        result = getattr(self.__font_module, name)
        self._logger.debug(result)
        return result

    def exposed_lcd_dimensions(self) -> ():
        self._logger.debug('lcd_dimensions')
        result = getattr(self.__lcd_module, 'dimensions')()
        self._logger.debug(result)
        return result

    def exposed_lcd_clear(self) -> bool:
        self._logger.debug('lcd_clear')
        getattr(self.__lcd_module, 'clear')()
        self.__lcd_cleared = True
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_lcd_show(self) -> bool:
        self._logger.debug('lcd_show')
        getattr(self.__lcd_module, 'show')()
        self.__lcd_cleared = False
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_lcd_set_pixel(self, x: int, y: int, state: bool) -> bool:
        if _TRACE:
            self._logger.debug('lcd_set_pixel: %s,%s with value: %s', str(x), str(y), str(state))
        if x < 0 or x > 127:
            raise ValueError(_PIXEL_ERROR_MSG)
        if y < 0 or y > 63:
            raise ValueError(_PIXEL_ERROR_MSG)
        v: int = 0
        if state:
            v = 1
        getattr(self.__lcd_module, 'set_pixel')(x, y, v)
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_lcd_set_pixels(self, x_tuple, y_tuple, state: bool) -> bool:
        self._logger.debug('lcd_set_pixels: %s for values: %s', state, str(len(x_tuple)))
        f = getattr(self.__lcd_module, 'set_pixel')
        v: int = 0
        if state:
            v = 1
        i: int = 0
        for x in x_tuple:
            if x < 0 or x > 127:
                raise ValueError(_PIXEL_ERROR_MSG)
            y = y_tuple[i]
            if y < 0 or y > 63:
                raise ValueError(_PIXEL_ERROR_MSG)
            f(x, y, v)
            i = i + 1
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_backlight_clear(self) -> bool:
        self._logger.debug('backlight_clear')
        for x in range(6):
            self.exposed_backlight_set_pixel(x, 0, 0, 0)
        self.__backlight_cleared = True
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_backlight_set_pixel(self, x: int, r: int, g: int, b: int) -> bool:
        if _TRACE:
            self._logger.debug('backlight_set_pixel: %s with color: %s,%s,%s', str(x), str(r), str(g), str(b))
        if x < 0 or x > 5:
            raise ValueError(_PIXEL_ERROR_MSG)
        if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
            raise ValueError(_COLOR_ERROR_MSG)
        getattr(self.__backlight_module, 'set_pixel')(x, r, g, b)
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_backlight_set_pixels(self, x_tuple, r: int, g: int, b: int) -> bool:
        self._logger.debug('backlight_set_pixels: %s,%s,%s for values: %s', r, g, b, str(len(x_tuple)))
        f = getattr(self.__backlight_module, 'set_pixel')
        for x in x_tuple:
            if x < 0 or x > 5:
                raise ValueError(_PIXEL_ERROR_MSG)
            if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
                raise ValueError(_COLOR_ERROR_MSG)
            f(x, r, g, b)
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_backlight_set_all(self, r: int, g: int, b: int) -> bool:
        if _TRACE:
            self._logger.debug('backlight_set_all with color: %s,%s,%s', str(r), str(g), str(b))
        if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
            raise ValueError(_COLOR_ERROR_MSG)
        getattr(self.__backlight_module, 'set_all')(r, g, b)
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_backlight_show(self) -> bool:
        self._logger.debug('backlight_show')
        getattr(self.__backlight_module, 'show')()
        self.__backlight_cleared = False
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_backlight_setup(self) -> bool:
        self._logger.debug('backlight_setup')
        getattr(self.__backlight_module, 'setup')()
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_touch_on(self, button: int, function: Any) -> bool:
        self._logger.debug('touch_on for button: %s', str(button))
        getattr(self.__touch_module, 'on')(button, function)
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_touch_setup(self) -> bool:
        self._logger.debug('touch_setup')
        getattr(self.__touch_module, 'setup')()
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_touch_set_led(self, led: int, state: bool) -> bool:
        if _TRACE:
            self._logger.debug('touch_set_led for led: %s with value: %s', str(led), str(state))
        v: int = 0
        if state:
            v = 1
        getattr(self.__touch_module, 'set_led')(led, v)
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_touch_set_leds(self, led_tuple, state: bool) -> bool:
        self._logger.debug('touch_set_leds: %s for values: %s', state, str(len(led_tuple)))
        f = getattr(self.__touch_module, 'set_led')
        v: int = 0
        if state:
            v = 1
        for led in led_tuple:
            f(led, v)
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_touch_enable_repeat(self, flag: bool) -> bool:
        self._logger.debug('touch_enable_repeat with value: %s', str(flag))
        getattr(self.__touch_module, 'enable_repeat')(flag)
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_touch_get_name(self, index: int) -> str:
        self._logger.debug('touch_get_name with value: %s', str(index))
        result = getattr(self.__touch_module, 'enable_repeat')(index)
        self._logger.debug(result)
        return result

    def exposed_touch_high_sensitivity(self) -> bool:
        self._logger.debug('touch_high_sensitivity')
        getattr(self.__touch_module, 'high_sensitivity')()
        # Always return a non None value for RPC unmarshalling
        return True

    def exposed_touch_set_repeat_rate(self, rate: int) -> bool:
        self._logger.debug('touch_set_repeat_rate with value: %s', str(rate))
        if rate < 35 or rate > 560:
            raise ValueError(_RATE_ERROR_MSG)
        getattr(self.__touch_module, 'set_repeat_rate')(rate)
        # Always return a non None value for RPC unmarshalling
        return True


class GfxHatFunctionProviderServiceMock(__AbstractGfxHatFunctionProviderService):

    def __init__(self, parent_logger: logging.Logger):
        super().__init__(parent_logger, _MOCK_MODULE)


class GfxHatFunctionProviderService(__AbstractGfxHatFunctionProviderService):

    class __TouchOnCallback(object):

        def __init__(self, logger: logging.Logger, button: int, f):
            self.__logger = logger
            self.__button: int = button
            self.__callback = rpyc.async_(f)

        def call(self, *args):
            if self.__callback:
                try:
                    self.__logger.debug('Invoking callback for button: %s with args: %s' % (str(self.__button), str(args)))
                    event = args[0]
                    self.__callback(getattr(event, 'channel'), getattr(event, 'event'))
                except Exception as ex:
                    _, _, exc_traceback = sys.exc_info()
                    traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
                    self.à_logger.error(ex)
            else:
                self.__logger.warn('Callback is disconnected for button: %s' % str(self.__button))

        def disconnect(self) -> None:
            self.__logger.debug('Disconnecting callback for button: %s' % str(self.__button))
            self.__callback = None

        def get_button(self) -> int:
            return self.__button

    def __init__(self, parent_logger: logging.Logger):
        super().__init__(parent_logger, _MODULE)
        self.__touch_on_callback: dict[int, self.__TouchOnCallback] = dict()

    def finalize(self) -> None:
        for v in self.__touch_on_callback.values():
            v.disconnect()
        super().finalize()

    def on_disconnect(self, conn: rpyc.Connection) -> None:
        super().on_disconnect(conn)
        for v in self.__touch_on_callback.values():
            v.disconnect()
        try:
            for x in range(6):
                self.exposed_touch_set_led(x, False)
                self.exposed_touch_on(x, None)
        except Exception as ex:
            _, _, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
            self._logger.error(ex)
        try:
            self.exposed_backlight_clear()
            self.exposed_backlight_show()
        except Exception as ex:
            _, _, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
            self._logger.error(ex)
        try:
            self.exposed_lcd_clear()
            self.exposed_lcd_show()
        except Exception as ex:
            _, _, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=6, file=sys.stderr)
            self._logger.error(ex)

    def exposed_touch_on(self, button: int, function: Any) -> bool:
        from id_function_invokers import FunctionInvokers
        f = function
        if FunctionInvokers.is_server():
            self._logger.debug('Using async callback function')
            if f is None:
                if button in self.__touch_on_callback:
                    self.__touch_on_callback[button].disconnect()
            else:
                cb = self.__TouchOnCallback(self._logger, button, rpyc.async_(f))
                self.__touch_on_callback[button] = cb
                f = cb.call
        return super().exposed_touch_on(button, f)
