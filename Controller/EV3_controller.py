# -*- coding: utf-8 -*-


#----------------------------------Libraries------------------------------------
#!/usr/bin/env pybricks-micropython
import ev3dev.ev3 as ev3
import time
import datetime import datetime as dt
import signal
import EV3_sensors
#----------------------------------I/O------------------------------------------

# Variables to be tested:
threshold = 10
baseSpeed = 80
turnAngle = 69

#THRESHOLD = (Max_Black_Value + Minimum_White_Value) /2 => (6 + 16) /2 = 10

# Motors initiliazation
mL = ev3.LargeMotor('outB')
mL.polarity = 'normal'

mR = ev3.LargeMotor('outC')
mR.polarity = 'normal'

# Sensors Initialization
colorSensorLeft = ev3.ColorSensor('in1')
assert colorSensorLeft.connected, "Left Color Sensor  is not connected"

colorSensorRight = ev3.ColorSensor('in4')
assert colorSensorRight.connected, "Right Color Sensor is not connected"

gyroSensor = ev3.GyroSensor('in3')
assert gyroSensor.connected, "Gyro Sensor is not connected"
gyroSensor.mode = 'GYRO-ANG'

#------------------------------------------------------------------------------
def signal_handler(sig, frame):
    print('Shutting down gracefully')
    mL.duty_cycle_sp = 0
    mR.duty_cycle_sp = 0
    exit(0)

# Install the signal handler for CTRL+C
signal.signal(signal.SIGINT, signal_handler)
print('Ctrl+C to exit')

#------------------------------------------------------------------------------

"""
    turnRight = 'R'
    turnLeft = 'L'
    goForward = 'F'
    goBackwards = 'B'
    turnAround = 'T'
    pushCan = 'C'
    goal = 'G'
"""

#------------------------------------------------------------------------------
class actionState(object):
    def __init__(self, action, repeatAction):
        self.action = action
        self.repeatAction = repeatAction

#------------------------------------------------------------------------------
def doAction(listofActions):
    actionList = []
    repeat = 1
    lengthOfList = len(listOfactions)

    for i in range(0,lengthOfList):
        if (i < lengthOfList-1):
            if (listOfactions[i] == listOfactions[i+1]):
                    repeat = repeat + 1
            else:
                actionList.append(actionState(listOfactions[i],repeat))
                repeat = 1
        else:
            actionList.append(actionState(listOfactions[i],repeat))
#actionList.append(actionState('G',1))
    return actionList
#------------------------------------------------------------------------------

# Either user input or read map solution
print("Enter 'sol' to read sokoban solution from file!")
print("Otherwise enter only valid action states: F, R, L, B, T")

user_input = input("Choice: ")
path = ""

if user_input == "sol":
    with open(user_input) as solution:
        path  = solution.read()
    solution.close()

else:
    path = user_input

complete = False

DOTHIS = doAction(path)
print("\n" + path)

print("-------------Robot now running-------------")

pointer = 0
startTime = dt.now()

while not complete:
    inputBehaviour = DOTHIS[pointer].action
    behaviourRepeat = DOTHIS[pointer].repeatAction
    print(inputBehaviour)

    if inputBehaviour == 'R':
        EV3_sensors.turnRight()

    elif inputBehaviour == 'L':
        EV3_sensors.turnLeft()

    elif inputBehaviour == 'F':
        EV3_sensors.goForward(repeatAction)

    elif inputBehaviour == 'F':
        EV3_sensors.goBackward(repeatAction)

    elif inputBehaviour == 'T':
        EV3_sensors.turnAround()

    elif inputBehaviour == 'C':
        EV3_sensors.pushCan()

    # Goal state
    elif inputBehaviour == 'G':
        complete = True

mL.duty_cycle_sp = 0
mR.duty_cycle_sp = 0

endTime = dt.now()

#------------------------------------------------------------------------------
