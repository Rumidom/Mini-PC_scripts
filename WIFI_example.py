import fontlib
import st7789 as st7789
import framebuf
import urequests
from machine import Pin, SPI
import json
import network
import time
import sys

screen_width = 240
screen_height = 240
screen_rotation = 3

wifi_ssid = 'YOURWIFISSID'
wifi_password = 'YOURWIFIPASSWORD'

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

display.fill(0)

white = st7789.color565(255, 255, 255)

wlan = network.WLAN(network.STA_IF)

def PrintToScreen(text,x,y):
    textW = screen_width
    textH = 8
    textBuffer = bytearray(screen_width * textH * 2) #two bytes for each pixel
    textfbuf = framebuf.FrameBuffer(textBuffer, textW, textH, framebuf.RGB565)
    IBM_font = fontlib.font("IBM BIOS (8,8).bmp") # Loads font to ram
    textfbuf.fill(0)
    fontlib.prt(text,x,0,1,textfbuf,IBM_font,color=white)
    display.blit_buffer(textBuffer, 0, y, textW, textH)

def PrintToScreenLarge(text,x,y):
    textW = screen_width
    textH = 16
    textBuffer = bytearray(screen_width * textH * 2) #two bytes for each pixel
    textfbuf = framebuf.FrameBuffer(textBuffer, textW, textH, framebuf.RGB565)
    IBM_font = fontlib.font("IBM BIOS (16,16).bmp") # Loads font to ram
    textfbuf.fill(0)
    fontlib.prt(text,x,0,1,textfbuf,IBM_font,color=white)
    display.blit_buffer(textBuffer, 0, y, textW, textH)
    
def ConnectToSSID(SSID,password=''):
    wlan.active(True)
    wlan.disconnect()
    wlan.connect(SSID, password)
    # Wait for connection.
    timeout = 0
    display.fill(0)
    while not wlan.isconnected():
        PrintToScreen(wifi_ssid,0,0)
        PrintToScreen('Connecting'+'.'*timeout,0,10)
        timeout += 1
        if timeout == 10:
            break
        time.sleep(1)
    if wlan.isconnected():
        display.fill(0)
        PrintToScreen('Connected!',0,0)
        PrintToScreen(str(wlan.ifconfig()[0]),0,10)
        time.sleep(4)
        return(True)
    else:
        display.fill(0)
        PrintToScreen("Connection Failed.",0,0)
        time.sleep(4)
        return(False)

# find your UTC offset here: https://en.wikipedia.org/wiki/List_of_UTC_offsets
def GetTime(UTC_offset = -3):
    url = 'https://time.now/developer/api/timezone/UTC'
    try:
        resp = urequests.get(url)
        unixtime = resp.json()['unixtime']
        offset_seconds = int(UTC_offset * 3600)
        if resp.status_code == 200:
            time.gmtime(time.time() + offset_seconds)
            return(True)
    except Exception as e:
        sys.print_exception(e, sys.stdout)
        return None
    
def TimeString():
    year = str(time.gmtime()[0])
    month = "%02d" % time.gmtime()[2]
    day = "%02d" % time.gmtime()[1]
    hour = "%02d" % time.gmtime()[3]
    minutes = "%02d" % time.gmtime()[4]
    seconds = "%02d" % time.gmtime()[5]
    return (hour+':'+minutes+':'+seconds)

def DateString():
    year = str(time.gmtime()[0])
    month = "%02d" % time.gmtime()[2]
    day = "%02d" % time.gmtime()[1]
    hour = "%02d" % time.gmtime()[3]
    minutes = "%02d" % time.gmtime()[4]
    seconds = "%02d" % time.gmtime()[5]
    return (day+'/'+month+'/'+year)

ConnectToSSID(wifi_ssid,password=wifi_password)
if wlan.isconnected():
    PrintToScreen('Getting The Time Online',0,20)
    GetTime()
    display.fill(0)
    while True:
        PrintToScreenLarge(TimeString(),54,100)
        PrintToScreenLarge(DateString(),38,120)