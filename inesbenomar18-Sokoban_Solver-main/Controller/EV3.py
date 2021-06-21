# -*- coding: utf-8 -*-

#----------------------------------Libraries------------------------------------
#!/usr/bin/env pybricks-micropython
import ev3dev.ev3 as ev3
import time
import signal
import datetime as dt

#----------------------------------I/O------------------------------------------

# Variables to be tested:
threshold = 6
baseSpeed = 80
turnAngle = 69


#threshold = 10
#baseSpeed = 80
#turnAngle = 69




# outerdegrees
# innerdegrees


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
    print('Shutting down')
    mL.duty_cycle_sp = 0
    mR.duty_cycle_sp = 0
    exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Ctrl+C to exit')

#------------------------------------------------------------------------------
# Function to evaluate EV3 battery state
def batteryState():
    power = ev3.PowerSupply()
    voltage = power.measured_voltage /100000

    if voltage < 8.0:
        print("State of battery: ")
        print ("   Under 8.0 Voltage at " + str(voltage))
        baseSpeed = 80

    else:
        print("State of battery: ")
        print ("   over 8.0 Voltage at " + str(voltage))
        baseSpeed = 80*0.9

batteryState()
#-------------------------------- Sensor Functions--------------------------------------

def readSensorsValues():
    sensorLeft = colorSensorLeft.value()
    sensorRight = colorSensorRight.value()

def readRight():
    return sensorRight.value()

def readLeft():
    return sensorLeft.value()

#-------------------------------- Motor Functions--------------------------------------

# Function to go straight
def goStraight(numberSquares):
    i = 0
    timer = time.time()
    while (i < numberSquares):
        sensorLeft = colorSensorLeft.value()
        sensorRight = colorSensorRight.value()

        print("sensorLeft: ", sensorLeft, " sensorRight: ", sensorRight, "  ", i)
        if sensorRight < threshold and sensorLeft < threshold and time.time() - timer > 0.5: # Pay attention to timer when base speed is high, risk robot having too many values and counting intersections that aren't there
            i = i + 1
            timer = time.time()

        if sensorRight < threshold:
            mR.duty_cycle_sp = baseSpeed * sensorRight / 4 # moins violent => plus petit dénominateur
                                                        #10
        else:
            mR.duty_cycle_sp = baseSpeed

        if sensorLeft < threshold:
            mL.duty_cycle_sp = baseSpeed * sensorLeft / 4
                                                       #10
        else:
            mL.duty_cycle_sp = baseSpeed


#------------------------------------------------------------------------------

# Function to go backwards
def goBackwards(numberSquares):

    mL.polarity = 'inversed'
    mR.polarity = 'inversed'

    i = 0
    timer = time.time()
    while (i < numberSquares):
        sensorLeft = colorSensorLeft.value()
        sensorRight = colorSensorRight.value()

        print("sensorLeft: ", sensorLeft, " sensorRight: ", sensorRight, "  ", i)
        if sensorRight < threshold and sensorLeft < threshold and time.time() - timer > 0.5: # Pay attention to timer when base speed is high, risk robot having too many values and counting intersections that aren't there
            i = i + 1
            timer = time.time()

        if sensorRight < threshold:
            mR.duty_cycle_sp =  baseSpeed/1.2 * sensorRight /6 # moins violent => plus petit dénominateur
        else:
            mR.duty_cycle_sp =  baseSpeed/1.2

        if sensorLeft < threshold:
            mL.duty_cycle_sp =  baseSpeed/1.2 * sensorLeft /6
        else:
            mL.duty_cycle_sp =  baseSpeed/1.2

#------------------------------------------------------------------------------
# Function to go turn left
# Using two motors

def turnLeft():
    sensorLeft = colorSensorLeft.value()
    sensorRight = colorSensorLeft.value()

    angleInit = gyroSensor.value() # read the value from gyro
    timer = time.time() # returns the number of seconds

# goes straight for a bit when it detects turn
    while (time.time() - timer) < 0.2 :
        mR.polarity = 'normal' #inversing the polarity of right motor
        mR.duty_cycle_sp = baseSpeed/2.5
        mL.duty_cycle_sp = baseSpeed/2.5

#then inverse
    mL.polarity = 'inversed'

    while(abs(gyroSensor.value() - angleInit) < turnAngle ): # Zone noire/ Intersection/ligne
        mR.duty_cycle_sp = baseSpeed/2.5 #dividing by 2.5 to account for gyro (big speed hinders turning angle)
        mL.duty_cycle_sp = baseSpeed/2.5

    mL.polarity = 'normal'
#------------------------------------------------------------------------------
# Function to turn right
# using two motors

def turnRight():
    sensorLeft = colorSensorLeft.value()
    sensorRight = colorSensorLeft.value()

    angleInit = gyroSensor.value()
    timer = time.time()

    while (time.time() - timer) < 0.2 :
        mL.polarity = 'normal'
        mL.duty_cycle_sp = baseSpeed/2.5
        mR.duty_cycle_sp = baseSpeed/2.5

    mR.polarity = 'inversed'

    while(abs(gyroSensor.value() - angleInit) < turnAngle ): # Zone noire/ Intersection/ligne
        mR.duty_cycle_sp = baseSpeed/2.5 #dividing by 2.5 to account for gyro (big speed hinders turning angle)
        mL.duty_cycle_sp = baseSpeed/2.5

    mR.polarity = 'normal'

#------------------------------------------------------------------------------
# Function to turn right
# using two motors

def turnAround():
    sensorLeft = colorSensorLeft.value()
    sensorRight = colorSensorLeft.value()

    angleInit = gyroSensor.value()
    timer = time.time()

    while (time.time() - timer) < 0.7 :
        mL.polarity = 'inversed'
        mR.polarity = 'inversed'
        mL.duty_cycle_sp = baseSpeed/2
        mR.duty_cycle_sp = baseSpeed/2
    mL.polarity = 'normal'
    mR.polarity = 'inversed'

    while(abs(gyroSensor.value() - angleInit) < 170 ): # Zone noire/ Intersection/ligne
        mR.duty_cycle_sp = baseSpeed/2.5 #dividing by 2.5 to account for gyro (big speed hinders turning angle)
        mL.duty_cycle_sp = baseSpeed/2.5

    mR.polarity = 'normal'

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
"""print("Enter 'sol' to read sokoban solution from file!")
print("Otherwise enter only valid action states: F, R, L, B, T")

user_input = input("Choice: ")
path = ""

if user_input == "F" or user_input == "B":
    repeat = input("How many squares: ")
    numOfSquares = int(repeat)

if user_input == "sol":
    with open(user_input) as solution:
        path  = solution.read()
    solution.close()

else:
    path = user_input

complete = False
print("\n" + path)"""

print("-------------Robot now running-------------")

pointer = 0
#startTime = dt.now()

#while not complete:

    # Get Robot moving
mL.run_direct()
mR.run_direct()



# 2020 map solution:

# 2020 map solution:

goStraight(3) #lll
turnLeft()
goStraight(1) #d
turnRight()
goStraight(5) #LLLL
turnAround()
goStraight(1)
turnLeft()
goStraight(1) #u
turnLeft()
goStraight(1) #l
turnLeft()
goStraight(3) #DD -1st can in Goal Position
turnAround()
goStraight(2)#u
turnRight()
goStraight(4) #rrrr
turnLeft()
goStraight(1) #u
turnRight()
goStraight(2) #rr
turnRight()
goStraight(2) #D
turnAround()
goStraight(1)
turnLeft()
goStraight(4) #llll
turnLeft()
goStraight(3) #ddd
turnLeft()
goStraight(2) #rr
turnLeft()
goStraight(1) #u
turnRight()
goStraight(1) #r
turnLeft()
goStraight(2) #U
turnAround()
goStraight(3) #dd
turnRight()
goStraight(3) #lll
turnRight()
goStraight(3) #uuu
turnRight()
goStraight(2) #rr
turnLeft()
goStraight(1) #u
turnRight()
goStraight(2) #rr
turnRight()
goStraight(1) #d
turnRight()
goStraight(5) #LLLL
turnAround()
goStraight(1)
turnLeft()
goStraight(1) #u
turnLeft()
goStraight(1) #l
turnLeft()
goStraight(3) #DD - 2nd can in Goal Position
turnAround()
goStraight(2)#u
turnRight()
goStraight(3) #rrr
turnLeft()
goStraight(1) #u
turnRight()
goStraight(4) #rrrr
turnRight()
goStraight(1) #d
turnRight()
goStraight(7) #LLLLLL
turnAround()
goStraight(1)
turnLeft()
goStraight(1) #u
turnLeft()
goStraight(1) #l
turnLeft()
goStraight(2) #D -- 3rd can in Goal Position
turnAround()
goStraight(1)
turnRight()
goStraight(7) #rrrrrrr
turnRight()
goStraight(1) #d
turnRight()
goStraight(3) #L
turnAround()
goStraight(1)
turnLeft()
goStraight(1) #u
turnLeft()
goStraight(4) #llll
turnLeft()
goStraight(3) #ddd
turnLeft()
goStraight(2) #rr
turnLeft()
goStraight(1) #u
turnRight()
goStraight(1) #r
turnLeft()
goStraight(2) #U
turnAround()
goStraight(1)
turnLeft()
goStraight(1) #r
turnLeft()
goStraight(1) #u
turnLeft()
goStraight(6) #LLLL
turnAround()
goStraight(1)
turnLeft()
goStraight(1) #u
turnLeft()
goStraight(1) #l
turnLeft()
goStraight(2) #D
turnAround()
goStraight(1)



"""    if user_input == 'R':
        turnRight()

    elif user_input == 'L':
        turnLeft()

    elif user_input == 'F':
        goStraight(numOfSquares)

    elif user_input == 'F':
        goBackward(numOfSquares)

    elif user_input == 'T':
        turnAround()

    elif user_input == 'C':
        pushCan()

    # Goal state
    elif user_input == 'G':
        complete = True"""

mL.duty_cycle_sp = 0
mR.duty_cycle_sp = 0

#endTime = dt.now()

#------------------------------------------------------------------------------

#print("\n\n------------------------ The End " + str(endTime.minute - startTime.minute) + ":" + str(abs(endTime.second - startTime.second)) + "------------------------\n")
