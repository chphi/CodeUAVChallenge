import MissionPlanner
import sys
from math import*
import clr
import time


print('start script')

a = Script.GetParam('RC3_MIN')
print a

Script.SendRC(7, 1300, True)
Script.Sleep(2000)
Script.SendRC(7,1100, True)


b = cs.ch8out
print b

#Script.ChangeParam('cs.ch8out',1900)
cs.ch8out = 1900
print cs.ch8out

Script.Sleep(1000)

cs.ch8out = 1567
print cs.ch8out


print('end script')