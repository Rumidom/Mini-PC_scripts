import os
import time
import st7789 as st7789
from machine import Pin, SPI
from ugif import gif

screen_width = 240
screen_height = 240
screen_rotation = 3

spi = SPI(1,
          baudrate=31250000,
          polarity=1,
          phase=1,
          bits=8,
          firstbit=SPI.MSB,
          sck=Pin(4),
          mosi=Pin(5))

display = st7789.ST7789(
    spi,
    screen_width,
    screen_height,
    reset=Pin(9, Pin.OUT),
    dc=Pin(8, Pin.OUT),
    backlight=Pin(7, Pin.OUT),
    rotation=screen_rotation)

def drawToScreen_PixelbyPixel(x, y, color):
    display.pixel(x, y, color)

display.fill(0)
gif_files = ['01.gif','02.gif','03.gif','04.gif']
gif_files.sort()

while True:
    for filepath in gif_files:
        gif_obj = gif('gifs/' + filepath)
        display.fill(0)
        gif_obj.BlitFrameToScreen(0, drawToScreen_PixelbyPixel)
        time.sleep(10)
