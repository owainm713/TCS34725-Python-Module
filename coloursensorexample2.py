#!/usr/bin/env python
"""coloursensorexample2, TCS34725 RGB colour sensor adafruit breakout
board practice using the TCS34725 python module

created Nov 7, 2017
modified Nov 18, 2017

"""

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

------------------------------------------------------------------------

In this example, the colour that is sensed by the sensor is reflected 3
ways

- pygame window with a square coloured to match the colour sensed
- common cathode tri-colour RGB LED illuminated to match the colour sensed
- a colour printed on the screen (not the pygame window) with the name of
the colour sensed.  Works ok for basic LEGO block colours, with more tweaking
and refining a larger range of colours could be identified

In this example, for the common cathode RGB I used 160ohm resistors between
the pi GPIO and each anode (i.e. the  R, G, B leads).

To get readings I always had the on-board LED on.

The matrix used to normalize the colour sensor readings is based on a matrix
found in a white paper on the TAOS website titled 'Color Sensing Using the
TCS230' by Charles Poynton. See page 15
"""

from TCS34725 import ColourSensor
import RPi.GPIO as GPIO
import pygame
import pygame.locals as GAME_GLOBALS
import pygame.event as GAME_EVENTS
import time, sys, smbus

#--- set up colour sensor ------------

address = 0x29   # colour sensor i2c address

CS = ColourSensor(address)
CS.set_a_time(atime=200) # set ATIME to 24ms, max count 10240
CS.set_wait_time(wtime=43.2,wlong=0)               # set WTIME to 43.2ms
CS.set_gain(4)                                     # set gain to 1x or 4x

# set interrupt and persistance levels
CS.set_interrupt_levels(lowTL = 56, highTL = 8000, persLevel = 3)

CS.set_enables(pon=1, aen=1, wen=1, aien=0)        # turn on PON, AEN and WEN

#--- set up RGB LED settings ---------

redLED = 26
greenLED = 16
blueLED =  22

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # uses numbering outside circles

GPIO.setup(redLED, GPIO.OUT)
redPWM = GPIO.PWM(redLED,500)
redPWM.start(0)

GPIO.setup(greenLED, GPIO.OUT)
greenPWM = GPIO.PWM(greenLED,500)
greenPWM.start(0)

GPIO.setup(blueLED, GPIO.OUT)
bluePWM = GPIO.PWM(blueLED,500)
bluePWM.start(0)

#--- set up pygame setttings ------------

pygame.init()

windowWidth = 400
windowHeight = 600

surface=pygame.display.set_mode((windowWidth,windowHeight)) # defines pygame window
pygame.display.set_caption('Colour Sensor Matching')

def normalize_readings(data, version=0):
    """normalize_readings,  function to normalize and modify values
    for use to display colour, returns values between 0 and 1"""
    
    if data[0] != 0:
        redS = float(data[1])/float(data[0])
        greenS = float(data[2])/float(data[0])
        blueS = float(data[3])/float(data[0])

        if version == 0:
            # pretty good for pygame translation using LEGO blocks
            
            red = redS*2.781 + greenS*-0.2407 + blueS*-0.4524
            green = redS*-0.4221 + greenS*2.577 + blueS*-0.6920
            blue = redS*-0.1366 + greenS*-0.8522 + blueS*2.3492

            red = red * 0.9
            green = green * 0.9
            blue = blue * 0.9
            
        elif version == 1:
            # pretty good LED translation using LEGO blocks
            
            red = redS*2.781 + greenS*0.2407 + blueS*-0.8524            
            green = redS*-0.4221 + greenS*2.377 + blueS*-0.7920            
            blue = redS*-0.4366 + greenS*-1.1522 + blueS*2.5492

            red = red * 0.9
            green = green * 0.9
            blue = blue * 0.9

        elif version == 2:
            # version based on version 0 for colour guessing - Nov 15, 2017

            red = redS*2.781 + greenS*-0.2407 + blueS*-0.4524
            green = redS*-0.4221 + greenS*2.577 + blueS*-0.6920
            blue = redS*-0.1366 + greenS*-0.8522 + blueS*2.3492

            red = red * 0.9
            green = green * 0.9
            blue = blue * 0.9
            
        else:
            red = redS
            green = greenS
            blue = blueS
        
    else:
        red, green, blue = 0, 0, 0

    #print(red,green,blue)

    #Correct any values that don't fall into the 0-1 range
        
    if red > 1:
        red = 1
    elif red < 0:
        red = 0

    if green > 1:
        green = 1
    elif green < 0:
        green = 0

    if blue > 1:
        blue = 1
    elif blue < 0:
        blue = 0
    

    return red, green, blue


def change_LED(red, green, blue):
    """change_LED, function to change a tri-colour LED to reflect the
    colour sensed by the colour sensor"""

    red = int(red*100)
    green = int(green*100)
    blue = int(blue*100)

    redPWM.ChangeDutyCycle(red)
    greenPWM.ChangeDutyCycle(green)
    bluePWM.ChangeDutyCycle(blue)

    #print(red,green,blue)

    return

def draw_rectangle(red, green, blue, square = 0):
    """draw_rectangle, function to draw a rectangle via pygame on the
    screen filled with the colour the colour sensor is sensing"""

    red = int(red*255)
    green = int(green*255)
    blue = int(blue*255)

    print(square,red,green,blue)

    if square == 0:
        pygame.draw.rect(surface,(red,green,blue),(100,100,200,200)) #draws rectangle
    else:
        pygame.draw.rect(surface,(red,green,blue),(100,400,200,200)) #draws rectangle
        
    pygame.display.update() # updates window

    return


def guess_colour(red, green, blue):
    """guess_colour2, function to figure out what colour is being read by
    the colour sensor and return the colour"""

    red = int(red*255)
    green = int(green*255)
    blue = int(blue*255)
    colourMatch = None

    colourList = []

    #Colour Name, Red Min, Red Max, Green Min, Green Max, Blue Min, Blue Max
    colourList.append(['Red', 231, 255, 0, 50, 0, 80])    
    colourList.append(['Orange',231,255,51,90,0,80])
    colourList.append(['Yellow',231,255,101,255,0,55])
    colourList.append(['Brown',231,255,91,120,41,80])
    colourList.append(['Light Yellow',176,230,101,190,0,55])

    colourList.append(['Purple',191,255,0,85,146,255])
    colourList.append(['Light Purple',101,191,51,110,101,190])
    colourList.append(['Dark Pink', 231, 255, 0, 90, 81, 145])
    colourList.append(['Light Pink', 181, 230, 0, 150, 101, 150])

    colourList.append(['Dark Blue',0,80,0,150,201,255])
    colourList.append(['Medium Blue',0,80,101,200,151,200])

    colourList.append(['Dark Green',0,100,191,255,0,75])
    colourList.append(['Medium Green',0,200,191,255,0,55])


    for colour in colourList:
        if red >= colour[1] and red <= colour[2]:           # check red component of colour
            if green >= colour[3] and green <= colour[4]:   # check green component of colour
                if blue >= colour[5] and blue <= colour[6]: # check blue component of colour
                    colourMatch = colour[0]
            

    return colourMatch

    

def quit_game():
    """quit_game, function to exit the program cleanly"""

    redPWM.stop()
    greenPWM.stop()
    bluePWM.stop()

    GPIO.cleanup()    
    pygame.quit()
    sys.exit()

    return

    

#------ main loop ---------------

try:
    while True:
        data = CS.read_CRGB()
        red, green, blue = normalize_readings(data)         # based on pygame translation
        redL, greenL, blueL = normalize_readings(data, 1)   # based on LED translation
        redG, greenG, blueG = normalize_readings(data, 2)   # based on colour guessing translation

        #uncomment the following 2 lines to see the raw data produced by the sensor        
        """print('Clear '+str(data[0])+' Red '+str(data[1])+' Green '+
              str(data[2])+' Blue '+str(data[3]))"""

        change_LED(redL, greenL, blueL)
        draw_rectangle(red, green, blue, 0)         # based on pygame translation
        #draw_rectangle(redW, greenW, blueW, 1)      # based on LED translation
        print(guess_colour(redG, greenG, blueG))    # based on colour guessing translation

        for event in GAME_EVENTS.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    break

            if event.type == GAME_GLOBALS.QUIT:
                break
            
        time.sleep(1)
        

except:
    pass

quit_game()


