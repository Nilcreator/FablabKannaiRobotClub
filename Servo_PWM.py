# -*- coding:utf-8 -*-

'''!
  @file demo_servo.py
  @brief Connect servo to one of pwm channels. All or part servos will sweep from 0 to 180 degrees.
  @n Test Servo: https://www.dfrobot.com/product-255.html
  @note Warning: Servos must connect to pwm channel, otherwise may destory Pi IO
  @n
  @copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license     The MIT License (MIT)
  @author      Frank(jiehan.guo@dfrobot.com)
  @version     V1.0
  @date        2019-3-28
  @url https://github.com/DFRobot/DFRobot_RaspberryPi_Expansion_Board
'''


import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from DFRobot_RaspberryPi_Expansion_Board import DFRobot_Expansion_Board_IIC as Board
from DFRobot_RaspberryPi_Expansion_Board import DFRobot_Expansion_Board_Servo as Servo

board = Board(1, 0x10)    # Select i2c bus 1, set address to 0x10
servo = Servo(board)

''' print last operate status, users can use this variable to determine the result of a function call. '''
def print_board_status():
  if board.last_operate_status == board.STA_OK:
    print("board status: everything ok")
  elif board.last_operate_status == board.STA_ERR:
    print("board status: unexpected error")
  elif board.last_operate_status == board.STA_ERR_DEVICE_NOT_DETECTED:
    print("board status: device not detected")
  elif board.last_operate_status == board.STA_ERR_PARAMETER:
    print("board status: parameter error")
  elif board.last_operate_status == board.STA_ERR_SOFT_VERSION:
    print("board status: unsupport board framware version")

if __name__ == "__main__":

  while board.begin() != board.STA_OK:    # Board begin and check board status
    print_board_status()
    print("board begin faild")
    time.sleep(2)
  print("board begin success")

  servo.begin()   # servo control begin

  while True:
    print("Servos sweeping from 0 to 180 degrees")
    for angle in range(0, 181, 1):  # Sweep from 0 to 180 degrees
      servo.move(0, angle)  # pwm0
      servo.move(1, 181-angle)  # pwm1
      servo.move(2, 181-angle)  # pwm2
      servo.move(3, angle)  # pwm3
      time.sleep(0.002) #Adjust timing so that each servo takes 2 seconds for sweeping

    time.sleep(2)
    print("Servos sweeping from 180 to 0 degrees")

    for angle in range(180, -1, -1):  # Sweep from 180 to 0 degrees
      servo.move(0, angle)  # pwm0
      servo.move(1, 181-angle)  # pwm1
      servo.move(2, 181-angle)  # pwm2
      servo.move(3, angle)  # pwm3
      time.sleep(0.002) #Adjust timing so that each servo takes 2 seconds for sweeping

    time.sleep(2)
