#!/usr/bin/python
# -*- coding: utf-8 -*-

# Get heading from a HMC5883L magnetometer connected via I2C
#
# Requires Adafruit_I2C from:
#  https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/tree/master/Adafruit_I2C
#
# The Adafruit_I2C module included with the BBB doesn't have the ability to change
# the endianness of the read 16-bit values
#

from Adafruit_I2C import Adafruit_I2C
import math
from time import sleep

mag = Adafruit_I2C(0x1e)

mag.write8(0x02, 0x00)

while 1: #                    X- Register               Z-Register                Y-Register
    (x, z, y) = ( mag.readS16(0x04, False), mag.readS16(0x06, False), mag.readS16(0x08, False))
    
    # Scaling valuesbased on defaults from datasheet
    x = x / 1100 * 100
    y = y / 1100 * 100
    z = z / 980 * 100
    
    # Convert X & Y angles to a heading
    headingRad = math.atan2(y,x) + (11+35/60) * (math.pi/180)
    # Correct for reversed heading
    if(headingRad < 0):
        headingRad += 2*math.pi
    
    # Check for wrap and compensate
    if(headingRad > 2*math.pi):
        headingRad -= 2*math.pi

    heading = headingRad * 180/math.pi
    
    print x, y, z, heading, "°"
    sleep(1)
