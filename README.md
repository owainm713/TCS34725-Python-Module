# TCS34725-Python-Module
Python 2.x Module for use with a TCS34725 colour sensor and the Raspberry Pi. I used an adafruit 
TCS34725 colour sensor breakout board.

To use this module, run your program as the root user,  i.e. sudo...

The module needs smbus to be installed to use the i2c interface. The i2c interface also 
needs to be enabled on your Raspberry Pi.

Also included is an example file that when run will output raw colour sensor data
every second. 

The connections to the adafruit TCS34725 colour sensor break out board I used
are as follows:
- TCS34725 LED connect to Gnd to turn off
- TCS34725 Int - not connected but could be connected any Pi GPIO and used
- TCS34725 SDA - Pi SDA
- TCS34725 SCL - Pi SCL
- TCS34725 3.3V - not connected
- TCS34725 Gnd - Pi Gnd
- TCS34725 Vin - Pi 3.3V

The i2c address for the TCS34725 colour sensor is 0x29.

The data sheet for the TCS34725 Colour sensor can be downloaded from the adafruit website

Current functions include:
- clear_interrupt()
- read_CRGB()
- read_status()
- set_enables(pon=0, aen=0, wen=0, aien=0)
- set_gain(gain=1)
- set_wait_time(wtime, wlong=0)
- set_a_time(atime)
- set_interrupt_levels(lowTL = 0, highTL = 65535, persLevel = 0)