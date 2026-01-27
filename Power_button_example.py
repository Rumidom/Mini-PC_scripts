import fontlib
import st7789 as st7789
import framebuf
from machine import Pin, SPI
import machine
import time
    
screen_width = 240
screen_height = 240
screen_rotation = 3

textH = 8
textW = 240

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
    #cs=Pin(9, Pin.OUT),
    dc=Pin(8, Pin.OUT),
    backlight=Pin(7, Pin.OUT),
    rotation=screen_rotation)

Power_button = Pin(3, Pin.IN, Pin.PULL_UP)
white = st7789.color565(255, 255, 255)

while True:
    if Power_button.value():
        display.fill(white)
    else:
        display.fill(0)






    