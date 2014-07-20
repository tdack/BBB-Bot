import serial, logging
import Adafruit_BBIO.UART as UART

class Sabertooth():
    """
        A class to control two motors using a Sabertooth 2x12 using the
        packetised serial mode.
        https://www.dimensionengineering.com/datasheets/Sabertooth2x12.pdf
    """

    cmds = {
            "fwd_left": 0x00,
            "rev_left": 0x01,
            "fwd_right": 0x04,
            "rev_right": 0x05,
            "ramp": 0x10
            }

    def __init__(self, Beagle_UART="UART1", port="/dev/ttyO1", address=128):
        """
            Beagle_UART - UART0, UART1 or UART2 on BeagleBone Black to use
            port        - /dev/ttyXX device to connect to
            address     - address of Sabertooth controller to send commands to
            
        """
        self.UART = Beagle_UART
        self.port = port
        self.address = address

        if (self.UART == None) or (self.port == None) or (self.address < 128 or self.address > 135):
            raise ("Invalid parameters")
            return None

        # Setup UART on BeagleBone (loads device tree overlay)
        UART.setup(self.UART)
        
        # Initialiase serial port
        self.saber = serial.Serial()
        self.saber.baudrate = 9600
        self.saber.port = '/dev/%s' % (self.port)
        self.saber.open()
        self.isOpen = self.saber.isOpen()
        return None
    
    def __del__(self):
        self.stop()
        return
    
    def sendCommand(self, command, message):
        """
            Sends a packetised serial command to the Sabertooth controller
            valid commands are (as strings):
                fwd_left, fwd_right, rev_left, rev_right, ramp
            message - speed to send with command 0-100 in % percent
        """
        checksum = (self.address + command + message) & 127
        sentBytes = self.saber.write("".join(chr(i) for i in [self.address, command, message, checksum]))
        self.saber.flush()
        return sentBytes

    def driveMotor(self, motor="both", direction="fwd", speed=0):
        """
            Simple motor control
            motor     - "left", "right" or "both"
            direction - "fwd" or "rev"
            speed     - 0 to 100 in percent
        """
        if (motor not in ["left", "right", "both"]) or (direction not in ["fwd", "rev"]):
            return -1

        if  speed < 0:
            speed = 0
        elif speed > 100:
            speed = 100
            
        speed = int((float(speed)* 127)//100)

        logging.debug("driveMotor: %s %d" %(direction + "_" + motor, speed))

        if motor == "both":
            sentBytes = self.sendCommand(self.cmds[direction + "_left"], speed)
            sentBytes += self.sendCommand(self.cmds[direction + "_right"], speed)
        else:
            sentBytes = self.sendCommand(self.cmds[direction + "_" + motor], speed)
        return sentBytes

    def stop(self):
        """
            Stops both motors
        """
        sentBytes = 0
        sentBytes = self.driveMotor("both", "fwd", 0)
        return sentBytes
    
    def setRamp(self, value):
        """
            Set acceleration ramp for controller
            value - ramp value to use
               1-10: Fast Ramp
              11-20: Slow Ramp
              21-80: Intermediate Ramp
        """
        sentBytes = 0
        if (value > 0 and value < 81):
            sentBytes = self.sendCommand(self.cmds["ramp"], value)
        return sentBytes
