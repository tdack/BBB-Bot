#!/usr/bin/python
import Adafruit_BBIO.ADC as ADC
from time import sleep

#
# For the BeagleBone Black the input voltage has to be 0-1.8V
# The easiest way is with a voltage divider
#
#              Ra             Rb
# Vin -->--[== 1K ==]--+--[== 560 ==]----+
#                      |                 |
#                      V                 |
#                      |                 |
#                     Vout              === Gnd
#                                        -
#           Rb
# Vout = --------- x Vin
#         Ra + Rb
#
# scale factor for voltage divider to get original Vin: (Ra+Rb)/Rb

class SharpIR(object):

    def __init__(self, AIN="AIN1", min=10, max=80, scale=2.5, coeff=28, power=-1):
        """
            min/max: minimum and maximum distances for the sensor
            scale: scaling factor to apply to measured voltages to convert
                   measured voltage to actual voltage. If sampled voltage is
                   coming from a voltage divider then scale = (Ra+Rb)/Rb
            coeff: coefficient determined from calibration
            power: powerterm determined from calibration
        """
        self.AIN = AIN
        self.min = min
        self.max = max
        self.scale = scale
        self.coeff = coeff
        self.power = power
        ADC.setup(AIN)
        return
        
    def calibrate(self, numsteps):
        """
            Calculates the coefficient and power terms for the sensor by recording
            voltage measurements at known distances and then performing an
            exponential curve fit on the data.
            
            numsteps: the number of measurements to take from min to max distance
                      more steps will give a more accurate curve
        """
        import numpy as np
        from scipy.optimize import curve_fit

        distances = range(self.min, self.max+1, (self.max-self.min)/numsteps)
        voltages = []
        
        def func(x, a, b):
            """
                Curve fitting function.  Used to fit data points to the curve
                y = a * x ^ b
            """
            return a * x ** b
        
        print('IR Calibration')
        print('\nThe calibration process requires you to place an object ' \
              '(a flat piece of card is good) at a variety of distances from ' \
              'the minumum distance to the maximum distance.\n\n' \
              'Voltage readings will be taken at (cm):')
        print distances
        
        for d in distances:
            print("Measure @ %d cm" % (d))
            sleep(5)
            for x in range(5):
                print("%d  " % (5-x))
                sleep(1)
                
            print("Reading @ %d cm" % (d))
            sleep(2)
            value = 0.0
            total = 0.0
            for x in range(5):
                value = ADC.read(self.AIN) * 1.8 * self.scale
                total = total + value
                print("#%d - %2.4f" % (x+1, value))
                sleep(1)
            print("%d cm Average: %2.4f" % (d, total/5))
            print"=" * 15
            voltages.append(total/5)
        
        # fits measured voltages to y = a * x ^ B curve
        popt, pcov = curve_fit(func, np.array(voltages), np.array(distances))
        self.coeff = popt[0]
        self.power = popt[1]
        print "Calibration Data"
        print "-" * 15
        print "Coefficient  :", self.coeff
        print "Power        :", self.power
        print "Err 1 std dev:", np.sqrt(np.diag(pcov))
        print "\nEquation     : distance = %2.2f * scaled_voltage ** %2.2f" % (self.coeff, self.power)
        print "-" * 15
        print "Example use:"
        print '  IR = SharpIR("P9_36", scale=1560.0/560.0, coeff=%2.6f, power=%2.6f)' % (self.coeff, self.power)
        print "-" * 15
        
    def distance(self):
        """
            Returns the distance in cm using the calibration data
        """
        distance = self.coeff * (ADC.read(self.AIN) * 1.8 * self.scale) ** self.power
        if distance < self.min:
            distance = -1       # invalid distance
        elif distance > self.max:
            distance = self.max
        return distance
        
if __name__ == '__main__':
    IR = SharpIR("P9_36", scale=1560.0/560.0)
    IR.calibrate(10)
    while 1:
        print IR.distance()
        sleep(1)