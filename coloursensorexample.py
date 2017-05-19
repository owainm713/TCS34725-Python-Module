#!/usr/bin/env python
"""coloursensorexample, TCS34725 RGB colour sensor adafruit breakout
board practice using the TCS34725 python module

created May 19, 2017"""

from TCS34725 import ColourSensor
import time, sys, smbus

address = 0x29

CS = ColourSensor(address)
CS.set_a_time(atime=24) # set ATIME to 24ms, max count 10240
CS.set_wait_time(wtime=43.2,wlong=0)               # set WTIME to 43.2ms
CS.set_gain(4)                                     # set gain to 4x

# set interrupt and persistance levels
CS.set_interrupt_levels(lowTL = 56, highTL = 8000, persLevel = 3)

CS.set_enables(pon=1, aen=1, wen=1, aien=0)        # turn on PON, AEN and WEN

try:
    while True:
        data = CS.read_CRGB()
        print('Clear '+str(data[0])+' Red '+str(data[1])+' Green '+
              str(data[2])+' Blue '+str(data[3]))
        time.sleep(1)

except:
    pass

print(bin(CS.read_status()))
CS.clear_interrupt()
print(bin(CS.read_status()))
del(CS)
