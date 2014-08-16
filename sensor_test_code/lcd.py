#!/usr/bin/python
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_CharLCD.Adafruit_CharLCD as Adafruit_CharLCD

lcd = Adafruit_CharLCD(pin_rs="P8_31", pin_e="P8_32", pins_db=["P8_27","P8_28","P8_29","P8_30"])
lcd.begin(16,2)
lcd.clear()
lcd.message("  Adafruit 16x2\n  Standard LCD")
