beaglebone-robot
================

A simple browser client that is able to send commands over web sockets to a BeagleBone Black running the server code.

## Client
Bootstrap/JQuery based web page that will connect to the server and send simple commands over web sockets to control the robot.

## Server
Control code written in Python.

Requires
1. Adafruit_BBIO Python library (installed by default on newer BeagleBone Black images)
2. Python json library (also installed by default)

## Robot
Simple two-wheel (differential drive) robot.  Motors are connected to a [Sabertooth 2x12](https://www.dimensionengineering.com/products/sabertooth2x12) motor controller allowing simple control and easy separation of voltages.

Control messages are sent to the controller using "packetised serial mode".

## Client-Server Communication
Control messages are passed from client to server as JSON over a web sockets transport.  Messages used are:

### Client -=> Server
```
    { event: 'drive',
        cmd: {
                direction: 'fwd|rev|left|right|stop|speed',
                speed: '0-100
            }
    }
````

### Server -=> Client
```
    { event: 'ack',
        cmd: {
                cmd: 'command and speed carried out'
            }
    }
````

```
    { event: 'obstacle',
       data: {
                sensor: 'sensor designation that obstacle was detected on'
            }
    }
````
