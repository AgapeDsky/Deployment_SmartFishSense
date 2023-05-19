import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# 19, 26
GPIO.setup(19, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

while(1):
  GPIO.output(19, 0)
  GPIO.output(26, 0)
  time.sleep(1)
  GPIO.output(19, 1)
  GPIO.output(26, 1)
  time.sleep(1)
