import RPi.GPIO as GPIO

but1 = 1
but2 = 7
GPIO.setmode(GPIO.BCM)

GPIO.setup(but1, GPIO.IN)
GPIO.setup(but2, GPIO.IN)

def but1_callback(channel):
   print("Button 1 Invoked!")
   return
def but2_callback(channel):
   print("Button 2 Invoked!")
   return

GPIO.add_event_detect(but1, GPIO.RISING, callback=but1_callback, bouncetime=100)
GPIO.add_event_detect(but2, GPIO.RISING, callback=but2_callback, bouncetime=100)

import time
while(True):
  time.sleep(1)
