#!/usr/bin/python
# -*- coding: utf-8 -*-

# Python library for HMC5883L magnetometer.

# Code based on:
# * http://think-bowl.com/i2c-python-libraries-for-the-raspberry-pi/ 
#   License: http://creativecommons.org/licenses/by-nc-sa/3.0/deed.en_US
#
# * https://github.com/adafruit/Adafruit_HMC5883_Unified 
#   License:
#        Permission is hereby granted, free of charge, to any person obtaining a
#        copy of this software and associated documentation files (the "Software"),
#        to deal in the Software without restriction, including without limitation
#        the rights to use, copy, modify, merge, publish, distribute, sublicense,
#        and/or sell copies of the Software, and to permit persons to whom the
#        Software is furnished to do so, subject to the following conditions:

#        The above copyright notice and this permission notice shall be included
#        in all copies or substantial portions of the Software.

#        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#        THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#        FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#        DEALINGS IN THE SOFTWARE.

from Adafruit_I2C import Adafruit_I2C
import math

class Adafruit_HMC5883L(object):

#   Default device address
    HMC5883_ADDRESS                            = (0x3C >> 1)

#   REGISTERS
    HMC5883_REGISTER_MAG_CRA_REG_M             = 0x00
    HMC5883_REGISTER_MAG_CRB_REG_M             = 0x01
    HMC5883_REGISTER_MAG_MR_REG_M              = 0x02
    HMC5883_REGISTER_MAG_OUT_X_H_M             = 0x03
    HMC5883_REGISTER_MAG_OUT_X_L_M             = 0x04
    HMC5883_REGISTER_MAG_OUT_Z_H_M             = 0x05
    HMC5883_REGISTER_MAG_OUT_Z_L_M             = 0x06
    HMC5883_REGISTER_MAG_OUT_Y_H_M             = 0x07
    HMC5883_REGISTER_MAG_OUT_Y_L_M             = 0x08
    HMC5883_REGISTER_MAG_SR_REG_Mg             = 0x09
    HMC5883_REGISTER_MAG_IRA_REG_M             = 0x0A
    HMC5883_REGISTER_MAG_IRB_REG_M             = 0x0B
    HMC5883_REGISTER_MAG_IRC_REG_M             = 0x0C
    HMC5883_REGISTER_MAG_TEMP_OUT_H_M          = 0x31
    HMC5883_REGISTER_MAG_TEMP_OUT_L_M          = 0x32

#   MAGNETOMETER GAIN SETTINGS
# See http://www.adafruit.com/datasheets/HMC5883L_3-Axis_Digital_Compass_IC.pdf
#                                                (Reg , factor)
    HMC5883_MAGGAIN_0_88                       = (0x00, 0.73)  # +/- 0.88
    HMC5883_MAGGAIN_1_3                        = (0x20, 0.92)  # +/- 1.3
    HMC5883_MAGGAIN_1_9                        = (0x40, 1.22)  # +/- 1.9
    HMC5883_MAGGAIN_2_5                        = (0x60, 1.52)  # +/- 2.5
    HMC5883_MAGGAIN_4_0                        = (0x80, 2.27)  # +/- 4.0
    HMC5883_MAGGAIN_4_7                        = (0xA0, 2.56)  # +/- 4.7
    HMC5883_MAGGAIN_5_6                        = (0xC0, 3.03)  # +/- 5.6
    HMC5883_MAGGAIN_8_1                        = (0xE0, 4.53)  # +/- 8.1
    
    HMC5883_MODE_CONTINUOUS                    = 0x00
    HMC5883_MODE_SINGLE                        = 0x01
    HMC5883_MODE_IDLE                          = 0x10

    def __init__(self, busnum=-1, debug=False, declination=(0,0)):
        self.bus = Adafruit_I2C(self.HMC5883_ADDRESS, busnum, debug)
        self.setDeclination(declination[0], declination[1])
        # Set initial scaling factor
        self.gain=self.HMC5883_MAGGAIN_1_3
        self.setScale(self.gain)
        # Set measurement mode to continuous intially
        self.setMode(self.HMC5883_MODE_CONTINUOUS)
        
        self.debug = debug

    def __str__(self):
        ret_str = ""
        (x, y, z) = self.getAxes()
        ret_str += "Axis X: "+str(x)+"\n"       
        ret_str += "Axis Y: "+str(y)+"\n" 
        ret_str += "Axis Z: "+str(z)+"\n" 
        ret_str += "Declination: "+ self.getDeclinationString() +"\n" 
        ret_str += "Heading: " + self.getHeadingString() + "\n" 
        return ret_str

    def setMode(self, mode=None):
        if mode == None:
            self.mode = self.HMC5883_MODE_SINGLE
        else:
            self.mode = mode
        self.bus.write8(self.HMC5883_REGISTER_MAG_MR_REG_M, self.mode)
 
    def setScale(self, gain):
        self.gain = gain
        self.setOption(self.HMC5883_REGISTER_MAG_CRB_REG_M, self.gain[0])

    def setOption(self, register, *function_set):
        options = 0x00
        for function in function_set:
            options = options | function
        self.bus.write8(register, options)

    # Adds to existing options of register	
    def addOption(self, register, *function_set):
        options = self.bus.read_byte(register)
        for function in function_set:
            options = options | function
        self.bus.write8(register, options)
    
    # Removes options of register	
    def removeOption(self, register, *function_set):
        options = self.bus.read_byte(register)
        for function in function_set:
            options = options & (function ^ 0b11111111)
        self.bus.write8(register, options)

    def setDeclination(self, degree, min = 0):
        self.declinationDeg = degree
        self.declinationMin = min
        self.declination = (degree+min/60) * (math.pi/180)
        
    def getDeclination(self):
        return (self.declinationDeg, self.declinationMin)
	
    def getDeclinationString(self):
        return str(self.declinationDeg)+"° "+str(self.declinationMin)+"'"

    # Returns heading
    def getHeading(self, DMS=False):
        (scaled_x, scaled_y, scaled_z) = self.getAxes()
        
        headingRad = math.atan2(scaled_y, scaled_x)
        headingRad += self.declination
        
        # Correct for reversed heading
        if(headingRad < 0):
            headingRad += 2*math.pi
        
        # Check for wrap and compensate
        if(headingRad > 2*math.pi):
            headingRad -= 2*math.pi
        
        # Convert to degrees from radians
        headingDeg = headingRad * 180/math.pi
        degrees = math.floor(headingDeg)
        minutes = round(((headingDeg - degrees) * 60))
        if DMS:
            return (degrees, minutes)
        else:
            return (headingDeg, 0.0)
	
    def getHeadingString(self):
        (degrees, minutes) = self.getHeading(True)
        return str(degrees)+"° "+str(minutes)+"'"
		
    def getAxes(self):
        (magno_x, magno_z, magno_y) = ( self.bus.readS16(self.HMC5883_REGISTER_MAG_OUT_X_H_M, False),
                                    self.bus.readS16(self.HMC5883_REGISTER_MAG_OUT_Z_H_M, False),
                                    self.bus.readS16(self.HMC5883_REGISTER_MAG_OUT_Y_H_M, False) )
        
        if (magno_x == -4096):
            magno_x = None
        else:
            magno_x = round(magno_x * self.gain[1], 4)
        
        if (magno_y == -4096):
            magno_y = None
        else:
            magno_y = round(magno_y * self.gain[1], 4)
        
        if (magno_z == -4096):
            magno_z = None
        else:
            magno_z = round(magno_z * self.gain[1], 4)
        
        return (magno_x, magno_y, magno_z)

# Simple example prints heading and x, y & z data once per second:
if __name__ == '__main__':

    from time import sleep

    # Set declination for your location as (degrees, minutes)
    # See http://magnetic-declination.com
    mag = Adafruit_HMC5883L(declination=(11,35))

    while True:
        print mag
        sleep(1) # Output is fun to watch if this is commented out
