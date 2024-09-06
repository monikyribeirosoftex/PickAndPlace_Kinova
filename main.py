
from machineRobot import MachineRobot
from realRobot import RealRobot
from testRobot import TestRobot


print("__MENU__")
name =  int(input("1 - Test Robot\n2 - Real Robot: "))

if name == 1:
    littleRobot = TestRobot()
elif name == 2:
    littleRobot = RealRobot()

machine = MachineRobot(littleRobot)
