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
import ntptime
import gc

screen_width = 240
screen_height = 240
screen_rotation = 3
max_chars_on_screen = 15 # 16x16 font
machine.freq(80000000) # seems more stable at lower freq

wifi_ssid = 'YOURWIFISSID'
wifi_password = 'YOURWIFIPASSWORD'

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
def handleInterrupt(pin):
    print("Powering Down")
    display.fill(0)
    machine.reset()
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
def handleInterrupt(pin):
    print("Powering Down")
    display.fill(0)
    machine.reset()
    
Power_button.irq(trigger=Pin.IRQ_FALLING, handler=handleInterrupt)

#white = st7789.color565(255, 255, 255)
light_gray = st7789.color565(180, 180, 180)
wlan = network.WLAN(network.STA_IF)
IBM_font_large = fontlib.font("IBM BIOS (16,16).bmp") # Loads font to ram
IBM_font_small = fontlib.font("IBM BIOS (8,8).bmp") # Loads font to ram

def printToScreen(text,x,y):
    textW = screen_width
    textH = 8
    textBuffer = bytearray(screen_width * textH * 2) #two bytes for each pixel
    textfbuf = framebuf.FrameBuffer(textBuffer, textW, textH, framebuf.RGB565)
    textfbuf.fill(0)
    fontlib.prt(text,x,0,1,textfbuf,IBM_font_small,color=light_gray)
    display.blit_buffer(textBuffer, 0, y, textW, textH)

def printToScreenLarge(text,x,y):
    textW = screen_width
    textH = 16
    textBuffer = bytearray(screen_width * textH * 2) #two bytes for each pixel
    textfbuf = framebuf.FrameBuffer(textBuffer, textW, textH, framebuf.RGB565)
    textfbuf.fill(0)
    fontlib.prt(text,x,0,1,textfbuf,IBM_font_large,color=light_gray)
    display.blit_buffer(textBuffer, 0, y, textW, textH)
    
def connectToSSID(SSID,password=''):
    wlan.active(False)
    wlan.active(True)
    #time.sleep(5)
    wlan.disconnect()
    wlan.connect(SSID, password)
    # Wait for connection.
    timeout = 0
    display.fill(0)
    while not wlan.isconnected():
        printToScreen(wifi_ssid,0,0)
        printToScreen('Connecting'+'.'*timeout,0,10)
        timeout += 1
        if timeout == 10:
            break
        time.sleep(1)
    if wlan.isconnected():
        display.fill(0)
        printToScreen('Connected!',0,0)
        printToScreen(str(wlan.ifconfig()[0]),0,10)
        time.sleep(4)
        return(True)
    else:
        display.fill(0)
        printToScreen("Connection Failed.",0,0)
        time.sleep(4)
        return(False)

# find your UTC offset here: https://en.wikipedia.org/wiki/List_of_UTC_offsets
def timeString(UTC_OFFSET=-3):
    offset_seconds = int(UTC_OFFSET * 3600)
    local_time = time.gmtime(time.time() + offset_seconds)
    hour = "%02d" % local_time[3]
    minutes = "%02d" % local_time[4]
    seconds = "%02d" % local_time[5]
    return (hour+':'+minutes+':'+seconds)

def dateString(UTC_OFFSET=-3):
    offset_seconds = int(UTC_OFFSET * 3600)
    local_time = time.gmtime(time.time() + offset_seconds)
    year = str(time.gmtime()[0])
    month = "%02d" % local_time[2]
    day = "%02d" % local_time[1]
    return (day+'/'+month+'/'+year)

def getNewsDict(UTC_OFFSET=-3):
    offset_seconds = int(UTC_OFFSET * 3600)
    local_time = time.gmtime(time.time() + offset_seconds)
    year = str(time.gmtime()[0])
    month = "%02d" % local_time[2]
    day = "%02d" % local_time[1]
    date = year+'-'+day+'-'+month
    #print("getting news for date:"+date)
    url = "https://news-agregator-rb77.onrender.com/api/"+date

    try:
        gc.collect()
        resp = requests.get(url,timeout=30)
        time.sleep(5)
        if resp != None:
            if resp.status_code == 200:
                
                return(resp.json())
            else:
                print(resp.text)
                return {'':[]}
    except Exception as e:
        sys.print_exception(e, sys.stdout)
        return {}

def scrollNews(News,source,headlineindex,scrollindex,y):
    if scrollindex == 0: # only prints once
        printToScreenLarge(source,screen_width//2-len(source)*8,y)
    headline = News[headlineindex]['title']
    init_hd_len = len(headline)
    headline = headline[:scrollindex]
    if scrollindex > max_chars_on_screen:
        hd_len = len(headline)
        headline = headline[hd_len-max_chars_on_screen:]       
        printToScreenLarge(headline,(hd_len-scrollindex)*17,y+25)
    else:
        printToScreenLarge(headline,(max_chars_on_screen-scrollindex)*17,y+25)

connectToSSID(wifi_ssid,password=wifi_password)
news_Flag = False
scrollindex = 0
source_index = 0
headlineindex = 0
news_dict = {}
sources_list = []
ntptime.settime()
display.fill(0)
last_time_string = ''
scroll_time_trigg = 0
gc.collect()

while True:
    time_string = timeString()
    date_string = dateString()
    
    if time_string != last_time_string:
        printToScreenLarge(time_string,54,100)
        last_time_string = time_string
        
    if time_string.split(':')[1] == '00':
        news_dict = {} # resets the news_dictionary every hour
    
    if news_dict == {}:
        printToScreenLarge(date_string,38,120) # no need to print every loop
        #printToScreenLarge('',2,150)
        news_dict = getNewsDict()
        gc.collect()
        if news_dict != {}:
            sources_list = list(news_dict.keys())
            print(sources_list)
        else:
            time.sleep(10)
    else:
        if source_index >= len(sources_list):
            source_index = 0
        source = sources_list[source_index]
        news = news_dict[source]
        if len(news) > 0:
            if time.ticks_ms() - scroll_time_trigg > 200:
                scroll_time_trigg = time.ticks_ms()
                headline_len = len(news[headlineindex]['title'])
                if scrollindex > headline_len+max_chars_on_screen+5:
                    headlineindex += 1
                    scrollindex = 0
                if headlineindex >= len(news):    
                    headlineindex = 0
                    source_index += 1
                    
                scrollNews(news,source,headlineindex,scrollindex,150)
                scrollindex += 1
        else:
            source_index += 1