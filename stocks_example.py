import fontlib
import st7789 as st7789
import framebuf
import urequests
from machine import Pin, SPI
import json
import network
import time
import sys
import machine

screen_width = 240
screen_height = 240
screen_rotation = 3

wifi_ssid = 'YOURWIFISSID'
wifi_password = 'YOURWIFIPASSWORD'
#you'll need to create a account here: https://api-ninjas.com/
#for free you get 3000 api calls per month
ninjas_apikey = 'YOURAPIKEY'


Power_button = Pin(3, Pin.IN, Pin.PULL_UP)

# waits for power button to be pressed
while not Power_button.value():
    pass

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

# interupt to reset the system when power button is turned off
def handle_interrupt(pin):
    print("Powering Down")
    display.fill(0)
    machine.reset()
    
Power_button.irq(trigger=Pin.IRQ_FALLING, handler=handle_interrupt)

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

def GetStockPrice(ticker,ApiKey):
    api_url = 'https://api.api-ninjas.com/v1/stockprice?ticker={}'.format(ticker)
    response = urequests.get(api_url, headers={'X-Api-Key': ApiKey})
    if response.status_code == 200:
        return(response.json())
    else:
        print("Error:", response.status_code, response.text)

ConnectToSSID(wifi_ssid,password=wifi_password)
if wlan.isconnected():
    PrintToScreen('Getting stock prices Online',0,20)
    display.fill(0)
    GoldPrice = GetStockPrice('GOLD',ninjas_apikey)['price']
    NVDAPrice = GetStockPrice('NVDA',ninjas_apikey)['price']
    SPVOOETFPrice = GetStockPrice('VOO',ninjas_apikey)['price']
    
    PrintToScreenLarge('GOLD {:.2f}'.format(GoldPrice),0,20)
    PrintToScreenLarge('NVIDEA {:.2f}'.format(NVDAPrice),0,45)
    PrintToScreenLarge('S&P5OO {:.2f}'.format(SPVOOETFPrice),0,70)