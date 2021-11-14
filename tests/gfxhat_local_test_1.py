#! /usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import os
import pathlib
import signal
import time
from logging.handlers import RotatingFileHandler
from id_function_invokers import FunctionInvokers
from function_providers.gfxhat_provider import GfxHatFunctionProvider
from PIL import Image, ImageDraw, ImageFont


def create_rotating_log() -> logging.Logger:
    # noinspection PyUnresolvedReferences
    log_file_path: str = '/tmp/gfxhat_test.log'
    result: logging.Logger = logging.getLogger("GfxHatTest")
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

FunctionInvokers.initialize(logger)
provider: GfxHatFunctionProvider = FunctionInvokers.get_provider(GfxHatFunctionProvider)

for x in range(6):
    provider.backlight_set_pixel(x, 0, 0, 0)
    provider.touch_set_led(x, False)
provider.backlight_show()
provider.lcd_clear()
provider.lcd_show()

logger.info("""hello-world.py
This basic example prints the text "Buon giorno" in the middle of the LCD
Press any button to see its corresponding LED toggle on/off.
Press Ctrl+C to exit.
""")

led_states = [False for _ in range(6)]
width, height = provider.lcd_dimensions()
image = Image.new('P', (width, height))
draw = ImageDraw.Draw(image)
draw.rectangle([(0, 0), image.size], fill=(0, 0, 0))
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16, encoding="unic")
text = "Buon giorno"
w, h = font.getsize(text)
x = (width - w) // 2
y = (height - h) // 2
draw.text((x, y), text, 1, font)


def touch_handler(*args):
    ch = args[0]
    event = args[1]
    if event == 'press':
        led_states[ch] = not led_states[ch]
        provider.touch_set_led(ch, led_states[ch])
        if led_states[ch]:
            provider.backlight_set_pixel(ch, 0, 255, 255)
        else:
            provider.backlight_set_pixel(ch, 0, 255, 0)
        provider.backlight_show()


for x in range(6):
    provider.touch_set_led(x, True)
    time.sleep(0.1)
    provider.touch_set_led(x, False)

for x in range(6):
    provider.backlight_set_pixel(x, 0, 255, 0)
    provider.touch_on(x, touch_handler)

provider.backlight_show()

print('Building lists of pixels')
pixel_x_on = list()
pixel_y_on = list()
pixel_x_off = list()
pixel_y_off = list()
for x in range(128):
    for y in range(64):
        pixel = image.getpixel((x, y))
        if pixel == 1:
            pixel_x_on.append(x)
            pixel_y_on.append(y)
        else:
            pixel_x_off.append(x)
            pixel_y_off.append(y)
print('Applying pixels')
provider.lcd_set_pixels(tuple(pixel_x_on), tuple(pixel_y_on), True)
provider.lcd_set_pixels(tuple(pixel_x_off), tuple(pixel_y_off), False)
provider.lcd_show()

print('Done')

try:
    signal.pause()
except KeyboardInterrupt:
    for x in range(6):
        provider.backlight_set_pixel(x, 0, 0, 0)
        provider.touch_set_led(x, False)
    provider.backlight_show()
    provider.lcd_clear()
    provider.lcd_show()
