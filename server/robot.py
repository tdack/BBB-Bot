#!/bin/python

import signal, sys, ssl, logging
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
from optparse import OptionParser
from sabertooth import Sabertooth
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import threading
from time import sleep
import json

# logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

class RobotControl(WebSocket):
    saber = None
    UART = "UART1"
    TTY  ="ttyO1"
    STOP_GPIO = "P9_13"
    STOP_BUTTON = "P9_15"
    
    PROXIMITY_GPIO = {"P9_11": {"name": "right"},
                      "P9_12": {"name": "left"}
                     }
                       
    LEDS_GPIO = { "RED_pin": "P8_10",
                  "GREEN_pin": "P8_11" }
    SPEAKER_PWM = "P8_13"
    SERVO_PWM = "P8_34"
    
    SPEED = 10
    CMD = None
    OBSTACLE = False
    SPEAKER = False
    SCAN = False
    angle = 0.0
    
    # cmd values that can be sent for a JSON "drive" event
    # maps command to corresponding function to control motors
    commands = {"fwd":   "do_forward",
                "rev":   "do_reverse",
                "left":  "turn_left",
                "right": "turn_right",
                "stop":  "do_stop",
                "speed": "set_speed"
               }

    def __init__(self, server, sock, address):
        super(RobotControl, self).__init__(server, sock, address)

        # setup GPIO pins for proximity sensors
        for PIN in self.PROXIMITY_GPIO:
            GPIO.setup(PIN, GPIO.IN)

        # try to add event detection for proximity GPIO pins
        for PIN, val in self.PROXIMITY_GPIO.items():
            # wait until the GPIO is configured as an input
            while GPIO.gpio_function(PIN) != GPIO.IN:
                GPIO.setup(PIN, GPIO.IN)
            GPIO.add_event_detect(PIN, GPIO.FALLING, self.__proximityDetect, 10)

        for LED in self.LEDS_GPIO.itervalues():
            GPIO.setup(LED, GPIO.OUT)
            GPIO.output(LED, GPIO.LOW)

        GPIO.setup(self.STOP_GPIO, GPIO.OUT)
        GPIO.output(self.STOP_GPIO, GPIO.HIGH)

        GPIO.setup(self.STOP_BUTTON, GPIO.IN)
        while GPIO.gpio_function(self.STOP_BUTTON) != GPIO.IN:
            GPIO.setup(self.STOP_BUTTON, GPIO.IN)
        GPIO.add_event_detect(self.STOP_BUTTON, GPIO.RISING, self.__stopButton, 10)
    
        PWM.start(self.SPEAKER_PWM, 50, 3000)
        PWM.stop(self.SPEAKER_PWM)
        self.SCAN = True
        threading.Thread(target=self.__servoScan).start()

        GPIO.output(self.LEDS_GPIO["RED_pin"], GPIO.HIGH)
        
        self.saber = Sabertooth(self.UART, self.TTY)
        self.saber.setRamp(15)

    def __speaker(self):
        if self.SPEAKER:
            return
        self.SPEAKER = True
        PWM.start(self.SPEAKER_PWM, 50, 3000)
        for dir in [-1,2]:
            for x in range(3,20):
                PWM.set_frequency(self.SPEAKER_PWM, 3000 + (dir * x * 100))
                sleep(0.05)
        PWM.stop(self.SPEAKER_PWM)
        self.SPEAKER = False
        return
            
    def __proximityDetect(self, channel):
        if self.OBSTACLE or (self.CMD in ["stop", None]):
            return # already handling a problem or not moving
        threading.Thread(target=self.__speaker).start()
        self.OBSTACLE = True
        self.sendJSON("obstacle", {"sensor": "%s" % (channel), 
                                   "name": "%s" % (self.PROXIMITY_GPIO[channel]["name"])})
        self.saber.driveMotor("both", "rev", int(float(self.SPEED)*1.5))
        delay = 1 - (float(self.SPEED)/200)
        sleep(delay)
        self.do_stop(self.SPEED)
        self.OBSTACLE = False
        return

    def __stopButton(self, channel):
        self.SCAN = False
        GPIO.output(self.STOP_GPIO, GPIO.HIGH)
        self.do_stop(self.SPEED)
        return

    def __servoScan(self):
        PWM.start(self.SERVO_PWM, 3, 50)
        while self.SCAN:
            for a in xrange(0,180,1):
                self.angle = a
                duty = 3.2 + (a/180.0)*10.5
                if self.SCAN:
                    PWM.set_duty_cycle(self.SERVO_PWM, duty)
                else:
                    break
                sleep(0.01)
            for a in xrange(181,1,-1):
                self.angle = a
                duty = 3.2 + (a/180.0)*10.5
                if self.SCAN:
                    PWM.set_duty_cycle(self.SERVO_PWM, duty)
                else:
                    break
                sleep(0.01)
        return

    def do_forward(self, set_speed):
        if set_speed != None:
            self.SPEED = set_speed
        self.saber.driveMotor("both", "fwd", self.SPEED)

    def do_reverse(self, set_speed):
        if set_speed != None:
            self.SPEED = set_speed
        self.saber.driveMotor("both", "rev", self.SPEED)

    def do_stop(self, set_speed):
        GPIO.output(self.LEDS_GPIO["RED_pin"], GPIO.HIGH)
        GPIO.output(self.LEDS_GPIO["GREEN_pin"], GPIO.LOW)
        self.saber.stop()

    def turn_left(self, set_speed):
        if set_speed != None:
            self.SPEED = set_speed
        self.saber.driveMotor("left", "fwd", self.SPEED)
        self.saber.driveMotor("right", "rev", self.SPEED)
        delay = 1 - (float(self.SPEED)/100)
        sleep(delay)
        if self.CMD in ["fwd", "rev"]:
            getattr(self, self.commands[self.CMD])(int(self.SPEED))
        else:
            self.do_stop(self.SPEED)

    def turn_right(self, set_speed):
        if set_speed != None:
            self.SPEED = set_speed
        self.saber.driveMotor("right", "fwd", self.SPEED)
        self.saber.driveMotor("left", "rev", self.SPEED)
        delay = 1 - (float(self.SPEED)/100)
        sleep(delay)
        if self.CMD in ["fwd", "rev"]:
            getattr(self, self.commands[self.CMD])(int(self.SPEED))
        else:
            self.do_stop(self.SPEED)
    
    def set_speed(self, new_speed):
        self.SPEED = new_speed
        if (self.CMD != "speed") and (self.CMD != None):
            getattr(self, self.commands[self.CMD])(int(self.SPEED))
    
    def sendJSON(self, event, data):
        try:
            self.sendMessage(json.dumps({"event": event, "data": data}))
        except Exception as n:
            print "sendJSON: ", n
    
    def handleMessage(self):
        if self.data is None:
            self.data = ''
        
        msg = json.loads(str(self.data))
        
        if msg['event'] == 'drive' and msg['data']['cmd'] in self.commands:
            if msg['data']['speed'] == None:
                msg['data']['speed'] = self.SPEED

            GPIO.output(self.LEDS_GPIO["RED_pin"], GPIO.LOW)
            GPIO.output(self.LEDS_GPIO["GREEN_pin"], GPIO.HIGH)
    
            getattr(self, self.commands[msg['data']['cmd']])(int(msg['data']['speed']))
            if msg['data']['cmd']  in ["fwd", "rev", "stop"]:
                self.CMD = msg['data']['cmd'] 
                self.SPEED = int(msg['data']['speed'])
            self.sendJSON("ack", {"cmd": "%s %d" % (self.commands[msg['data']['cmd']], self.SPEED)})
        elif (msg["event"] == 'fetch') and (msg['data']['cmd'] == 'angle'):
            self.sendJSON("angle", {"angle": "%2.f" % (self.angle)});

    def handleConnected(self):
        print self.address, 'connected'

    def handleClose(self):
        for PIN in self.PROXIMITY_GPIO:
            GPIO.remove_event_detect(PIN)
        GPIO.remove_event_detect(self.STOP_BUTTON)
        PWM.stop(self.SPEAKER_PWM)
        self.SCAN = False
        PWM.stop(self.SERVO_PWM)
        self.saber.stop()
        print self.address, 'closed'

if __name__ == "__main__":

    def close_sig_handler(signal, frame):
        GPIO.cleanup()
        PWM.cleanup()
        server.close()
        sys.exit()
    
    parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
    parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
    parser.add_option("--port", default=8000, type='int', action="store", dest="port", help="port (8000)")
    parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
    parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert", help="cert (./cert.pem)")
    parser.add_option("--ver", default=ssl.PROTOCOL_TLSv1, type=int, action="store", dest="ver", help="ssl version")
    
    (options, args) = parser.parse_args()
    
    cls = RobotControl
    
    if options.ssl == 1:
        server = SimpleSSLWebSocketServer(options.host, options.port, cls, options.cert, options.cert, version=options.ver)
    else:	
        server = SimpleWebSocketServer(options.host, options.port, cls)

    signal.signal(signal.SIGINT, close_sig_handler)

    print "Starting robot control server.  Listening on ws://%s:%d" % (options.host, options.port)
    server.serveforever()