#!/usr/bin/env python
"""TCS34725, python moduel for the TCS34725 RGB colour sensor adafruit
breakout board.

created May 19, 2017"""

"""
Copyright 2017 Owain Martin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import time, sys, smbus

class ColourSensor:

    def __init__(self, i2cAddress):

        self.address = i2cAddress
        self.bus =smbus.SMBus(1)

        return

    def single_access_read(self, reg=0x00):
        """single_access_read, function to read a single data register
        of the TCS34725 RGB colour sensor"""

        cmdBit = 0b1 # cmd bit set to 1
        msBit = 0b01  # multiple read/write address increment select bits set to auto increment

        cmd = (cmdBit<<7)+(msBit<<5)+reg              
       
        dataTransfer=self.bus.read_byte_data(self.address,cmd)
        
        return dataTransfer

    def single_access_write(self, reg=0x00, regValue=0x0):
        """single_access_write, function to write a single data register
        of the TCS34725 RGB colour sensor"""

        cmdBit = 0b1 # cmd bit set to 1
        msBit = 0b01  # multiple read/write address increment select bits set to auto increment

        cmd = (cmdBit<<7)+(msBit<<5)+reg

        self.bus.write_byte_data(self.address, cmd, regValue)

        return

    def convert_value(self, lowByte, highByte):
        """convert_value,  add low and high bytes of data together to
        provide output"""

        value = (highByte<<8) + lowByte        

        return value

    def clear_interrupt(self):
        """clear_interrupt, function to clear the interrupt condition"""

        cmdBit = 0b1 # cmd bit set to 1
        msBit = 0b11  # multiple read/write address increment select bits set to special function

        cmd = (cmdBit<<7)+(msBit<<5)+0b00110           
       
        dataTransfer=self.bus.read_byte_data(self.address,cmd)

        return

    def read_CRGB(self):
        """read_CRGB, function to read the clear, red, green and blue
        output data from the sensor"""

        output=[]

        clearLow = self.single_access_read(0x14)
        clearHigh = self.single_access_read(0x15)
        redLow = self.single_access_read(0x16)
        redHigh = self.single_access_read(0x17)
        greenLow = self.single_access_read(0x18)
        greenHigh = self.single_access_read(0x19)
        blueLow = self.single_access_read(0x1A)
        blueHigh = self.single_access_read(0x1B)

        output.append(self.convert_value(clearLow, clearHigh))
        output.append(self.convert_value(redLow, redHigh))
        output.append(self.convert_value(greenLow, greenHigh))
        output.append(self.convert_value(blueLow, blueHigh))

        return output

    def read_status(self):
        """read_status, function to read the status register 0x13"""

        status = self.single_access_read(0x13)

        return status

    def set_enables(self, pon=0, aen=0, wen=0, aien=0):
        """set_enables, function to set the 4 different enables in the
        enable register (0x00)"""

        if pon != 1:
            pon = 0

        if aen != 1:
            aen = 0

        if wen !=1:
            wen = 0

        if aien !=1:
            aien = 0

        enableBits = (aien<<4)+(wen<<3)+(aen<<1)+pon

        self.single_access_write(0x00, enableBits)

        return

    def set_gain(self, gain=1):
        """set_gain, function to set the sensors gain level, valid levels
        are 1, 4, 16 and 60, this sets bits 0 & 1 of register 0x0F"""

        if gain == 60:
            gainBits = 0b11
        elif gain == 16:
            gainBits = 0b10
        elif gain == 4:
            gainBits = 0b01
        else:  # gain = 1
            gainBits = 0b00

        self.single_access_write(0x0F, gainBits)

        return

    def set_wait_time(self, wtime, wlong=0):
        """set_wait_time, function to set the sensor wait time, i.e. the
        time between readings. wtime value passed in the function call is in ms."""

        # with wlong = 0, wait time range from 2.4ms to 614ms in 2.4ms increments
        # with wlong = 1, wait time range from 0.029s to 7.4ms in 28.8ms increments

        # set wlong bit, bit 1,  in the Configuration Register (0x0D)

        if wlong !=1:
            wlong = 0

        self.single_access_write(0x0D, (wlong<<1))

        # wait time register (0x03)    

        step = int(256 - (wtime // 2.4))    

        self.single_access_write(0x03, step)

        return    
        
    def set_a_time(self, atime):
        """set_a_time, function to set the sensor ATIME, i.e. the
        time to take a reading. This sets RGBC Timing Register (0x01).
        atime value passed in the function call is in ms."""

        # the output max count changes with atime.
        # max count = (256 - atime/2.4)X1024 to a max of 65535
        
        step = int(256 - (atime // 2.4))        

        self.single_access_write(0x01, step)

        return

    def set_interrupt_levels(self, lowTL = 0, highTL = 65535, persLevel = 0):
        """set_interrupt_levels, function to set the clear channel low and
        high threshold levels as well as interrupt persistance level. This
        sets registers 0x04-0x07 and 0x0C"""

        if lowTL < 0:
            lowTL = 0
        elif lowTL > 65535:
            lowTL = 65535

        if highTL < 0:
            highTL = 0
        elif highTL > 65535:
            highTL = 65535

        lowTLLowByte = lowTL & 0xFF
        lowTLHighByte = (lowTL & 0xFF00)>>8

        highTLLowByte = highTL & 0xFF
        highTLHighByte = (highTL & 0xFF00)>>8

        #print(hex(lowTLLowByte),hex(lowTLHighByte))  # for testing

        self.single_access_write(0x04, lowTLLowByte)
        self.single_access_write(0x05, lowTLHighByte)
        self.single_access_write(0x06, highTLLowByte)
        self.single_access_write(0x07, highTLHighByte)

        persistanceLevels = [(0,0b0),(1,0b1),(2,0b10),(3,0b11),(5,0b100),
                             (10,0b101),(15,0b110),(20,0b111),(25,0b1000),
                             (30,0b1001),(35,0b1010),(40,0b1011),(45,0b1100),
                             (50,0b1101),(55,0b1110),(60,0b1111)]

        perBits =0b0

        for level in persistanceLevels:
            if level[0] == persLevel:
                perBits = level[1]

        self.single_access_write(0x0C, perBits)     

        return

    def __del__(self):
        """__del__, cleanup i2c connections"""

        self.set_enables(pon=0, aen=1, wen=1, aien=0)   # turn off PON         
        self.bus.close()

        return

if __name__ == "__main__":

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

