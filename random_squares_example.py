import math
import st7789 as st7789
import framebuf
from machine import Pin, SPI
import random
import time

screen_width = 240
screen_height = 240
max_sqsz = 50
min_sqsz = 10

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
    #cs=Pin(9, Pin.OUT),
    dc=Pin(8, Pin.OUT),
    backlight=Pin(7, Pin.OUT),
    rotation=screen_rotation)

while True:
    display.fill(0)
    for i in range(10):
        color =  st7789.color565(
                    random.getrandbits(8),
                    random.getrandbits(8),
                    random.getrandbits(8),
                )
        
        sqsz = random.randint(min_sqsz, max_sqsz)
        px = random.randint(0, screen_width-1)
        py = random.randint(0, screen_height-1)
        #print(px,py,sqsz,sqsz,color)
        # For some reason same squares abort printing
        # Resulting in retangles
        # SPI failure?
        display.fill_rect(px,py,sqsz,sqsz,color)
        time.sleep(0.5)
    
