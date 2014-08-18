#!/bin/python
import Adafruit_BBIO.GPIO as GPIO
from Adafruit_CharLCD import Adafruit_CharLCD as LCD
# Import the eQEP driver
from eqep import eQEP

MENU = ["1. Item 1",
        "2. Item 2",
        "3. Item 3",
        "4. Item 4"]

CURSOR_INDEX = 1
MENU_TOP = 1

LINES = 2

lcd = LCD()
lcd.begin(16,2)
lcd.blink()

encoder0 = eQEP("/sys/devices/ocp.3/48300000.epwmss/48300180.eqep", eQEP.MODE_ABSOLUTE)

# Set the polling period of the encoder to 0.1 seconds, or 100,000,000 nanoseconds
encoder0.set_period(100000000)

def displayMenu(top, lines):
    top -= 1
    lcd.clear()
    if top+lines > len(MENU):
        top = len(MENU) - lines
    for x in range(lines):
        lcd.setCursor(0,x)
        lcd.message(MENU[top + x])


displayMenu(1, LINES)
lcd.setCursor(0, CURSOR_INDEX - 1)

# Poll the position indefinitely.  Program will provide a position at 10 Hz
while True:
    delta = encoder0.poll_relposition()

    CURSOR_INDEX += delta
    if delta == 1:
        if CURSOR_INDEX > LINES:
            CURSOR_INDEX = LINES
            MENU_TOP += 1
            if MENU_TOP > len(MENU):
                MENU_TOP = len(MENU) - LINES
    elif delta == -1:
        if CURSOR_INDEX < 1:
            CURSOR_INDEX = 1
            MENU_TOP -= 1
            if MENU_TOP < 1:
                MENU_TOP = 1
                
    if delta != 0:
        displayMenu(MENU_TOP, LINES)
        lcd.setCursor(0, CURSOR_INDEX - 1)
        print "Cursor: %d\tMenu: %d" % (CURSOR_INDEX, MENU_TOP)