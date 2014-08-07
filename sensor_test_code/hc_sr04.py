#!/usr/bin/env python

# Crude distance measurement using an HC-SR04 ultrasonic sonar
#
# P9_14 - Output - Trigger to HC-SR04
# P8_15 - Input  - Echo signal from HC-SR04
#
# Echo line needs to be level shifted from 5V down to 3.3V for the BBB
#
#   Echo -->--[==2K2==]---+---[==2K2==]-->--GND
#                         |
#                         V
#                         +-->--P8_15
#
# The accuracy of this method is not great.  Distances less than about 20cm
# cause erroneous measurements - the timing is simply not accurate enough to
# measure short distances

import Adafruit_BBIO.GPIO as GPIO
from datetime import datetime
import time

def Count(channel):
    # Get time when Echo line goes high (ie: RISING edge)
    if GPIO.input("P8_15") == GPIO.HIGH and not Count.counting:
        Count.startTime = datetime.now()
        Count.counting = True
    # Get time when Echo line goes low (ie: FALLING edge)
    elif GPIO.input("P8_15") == GPIO.LOW and Count.counting:
        Count.endTime = datetime.now()
        # delta is the period of the echo (roughly)
        Count.delta = Count.endTime - Count.startTime
        Count.counting = False
    return

# Initialise the Count() callback function variables
Count.counting = False
Count.startTime = None
Count.endTime = None
# This keeps Python happy and makes delta a datetime.timedelta type
Count.delta = datetime.now() - datetime.now()

# Trigger output pin
GPIO.setup("P9_14", GPIO.OUT)

# Echo input pin - remember to level shift to 3.3V
GPIO.setup("P8_15", GPIO.IN)
# Sometimes it takes a little while for the GPIO to be setup and adding event
# detection fails, so we'll go around in circles until the GPIO is ready
while GPIO.gpio_function("P8_15") != GPIO.IN:
    GPIO.setup("P8_15", GPIO.IN)

# Python bindings can only handle one event per GPIO, so bind to both
# the callback function will work out if it is rising or falling.
GPIO.add_event_detect("P8_15", GPIO.BOTH, Count, 1)

# Set trigger to LOW initially
GPIO.output("P9_14", GPIO.LOW)

try:
    while 1:
        # We'll take an average over 3 measurements
        total = 0
        for x in range(0,3):
            # Set Trigger to HIGH
            GPIO.output("P9_14", GPIO.HIGH)
            # Wait a tiny amount (should be 10us). This is not deterministic
            # when running stock Linux. To get better use a RTOS or the PRUSS
            time.sleep(0.001)
            # Set Trigger to LOW
            # This will cause the HC-SR04 to output an ultrasonic pulse and start
            # listening for the return
            GPIO.output("P9_14", GPIO.LOW)
            # Sleep for a bit so that we don't send out another pulse before the
            # previous one has finished
            time.sleep(0.05)
            # 58.77 is the magic number for cm per microsecond
            total = total + Count.delta.microseconds/58.77
        distance = min(200.0, max(total/3.0,17.0))
        print "Distance: %2.2f cm" % distance
except (KeyboardInterrupt, SystemExit):
    GPIO.cleanup()
except:
    raise()
    
GPIO.cleanup()
