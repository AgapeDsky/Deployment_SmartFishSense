import cv2
import time
import numpy as np
import pandas as pd
import smbus
from gpiozero import Button
import RPi.GPIO as GPIO
import tensorflow as tf
import pymongo
from datetime import datetime

# program to transmit data, for logging and training purposes
# each sensor has its own topic
#     topics: "f n", with n integer 1->20 (topic for each frames of video)
#             "acc o", with o axis (x,y,or z) (topic for each axis of accelerometer)
# mqtt host: 192.168.1.115 (static, lab's main computer)

# initialize GPIO outputs
GPIO.setmode(GPIO.BCM)
LED_1 = 19
LED_2 = 26
FEED_CMD = 17
GPIO.setup(LED_1, GPIO.OUT)
GPIO.setup(LED_2, GPIO.OUT)
GPIO.setup(FEED_CMD, GPIO.OUT)

# initialize button GPIO
EXIT_IDLE_CMD = 1
RESET_CMD = 7
GPIO.setup(EXIT_IDLE_CMD, GPIO.IN)
GPIO.setup(RESET_CMD, GPIO.IN)

# add interrupt event for buttons
exit_idle_but = 0
reset_but = 0
def exit_idle_call(channel):
   global exit_idle_but
   exit_idle_but = 1
   print("EXIT IDLE BUT INVOKED!")
   return
GPIO.add_event_detect(EXIT_IDLE_CMD, GPIO.RISING, callback=exit_idle_call, bouncetime=100)
def reset_call(channel):
   global reset_but
   reset_but = 1
   print("RESET BUT INVOKED!")
   return
GPIO.add_event_detect(RESET_CMD, GPIO.RISING, callback=reset_call, bouncetime=100)

# accelerometer sensor register addresses
BASE_ADDR = 0x68
ACC_X_H = 0x3B
ACC_X_L = 0x3C
ACC_Y_H = 0x3D
ACC_Y_L = 0x3E
ACC_Z_H = 0x3F
ACC_Z_L = 0x40
PWR_MGMT_1 = 0x6B

# initialize I2C Protocol
i2c = smbus.SMBus(1)

# i2c calls
def read_i2c(reg_addr):
    return i2c.read_byte_data(BASE_ADDR, reg_addr)
def write_i2c(reg_addr, val):
    return i2c.write_byte_data(BASE_ADDR, reg_addr, val)

# initialize accelerometer
write_i2c(PWR_MGMT_1, 0)

# retrieve model
model = tf.keras.models.load_model("/home/pi2/Deployment_SmartFishSense/Model_TA/")

# establish cloud connection
uri = "mongodb+srv://agapedsky:dagozilla@cluster0.ro1gcoc.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(uri)
db = client.TA
push_db = db.data2
pull_db = db.data1

# mongodb variables
reset_web = 0
exit_idle_web = 0

############# main ###############
#define operational state and params
IDLE = 0
OPERATIONAL = 1
COUNT_THRESHOLD = 12 #3 hrs / 15 mins

STIMULI_TIME_S = 2.
FEED_TIME_S = 5.

SIZE = (300,300)
MAX_FRAME = 20
SIGNAL_FACTOR = 0.

count = 0
cur_state = 0
next_state = 0
confidence = 0
exit_idle = 0
reset = 0

# initialization
cam = cv2.VideoCapture(0)

# functions
def get_next_state():
    global count, cur_state, exit_idle, reset

    next_state = cur_state

    # idle state
    if cur_state == IDLE:
        if exit_idle or (count>COUNT_THRESHOLD):
            next_state = OPERATIONAL
        else:
            count = count+1
            next_state = IDLE

    # operational state
    elif cur_state == OPERATIONAL:
        next_state = IDLE

    # return next state
    return next_state

def delta(val,n1,n2=0,edge=0):
    # edge = 1: first and last data only
    temp_val = abs(val-n1)
    if edge:
        if(temp_val > 65535 - temp_val):
            return 65535 - temp_val
        else : return temp_val
    else:
        temp_val_1 = abs(val-n1);
        if (temp_val_1 == temp_val_1 > 65535 - temp_val_1) :
            temp_val_1 = 65535 - temp_val_1
        temp_val_2 = abs(val-n2);
        if temp_val_2 == temp_val_2 > 65535 - temp_val_2:
            temp_val_2 = 65535 - temp_val_2
        return 0.5*(temp_val_1+temp_val_2)

def process_loop():
    global cam, reset, exit_idle

    GPIO.output(LED_1, 1)
    print("Process Loop Invoked!")

    if cur_state == OPERATIONAL:
        print("OPERATIONAL PROCESS BEGINS")
        # validate cam
        if (cam.isOpened()):
            lapar = True
            confidence = False
            while lapar:
                push_srv()

                # initialize data frames
                frames = []
                acc_x = []
                acc_y = []
                acc_z = []
                
                # give stimuli
                if not(confidence):
                    give_stimuli()
                
                # log data
                for i in range(20):
                    ret, frame = cam.read()
                    if ret==True:
                        frames.append(frame)
                        cur_acc_x = ((read_i2c(ACC_X_H) << 8)|read_i2c(ACC_X_L))
                        cur_acc_y = ((read_i2c(ACC_Y_H) << 8)|read_i2c(ACC_Y_L))
                        cur_acc_z = ((read_i2c(ACC_Y_H) << 8)|read_i2c(ACC_Z_L))

                        acc_x.append((cur_acc_x))
                        acc_y.append((cur_acc_y))
                        acc_z.append((cur_acc_z))

                        time.sleep(0.05)

                print("Read Done")
                
                # preprocess video data
                cropped_frames = []
                for frame in frames:
                    frame = frame[200:850, 100:960]
                    frame = cv2.resize(frame,SIZE)
                    cropped_frames.append(frame)
                video = []
                video.append(cropped_frames)
                video = np.array(video)
                
                # preprocess accelerometer data
                acc_x_new = []
                acc_y_new = []
                acc_z_new = []

                temp = []
                for i in range(20):
                    if i == 0:
                        temp.append( delta(acc_x[i],acc_x[i+1],edge=1) * SIGNAL_FACTOR )
                    elif i == 19:
                        temp.append( delta(acc_x[i],acc_x[i-1],edge=1) * SIGNAL_FACTOR )
                    else:
                        temp.append( delta(acc_x[i],acc_x[i-1], acc_x[i+1]) * SIGNAL_FACTOR )
                acc_x_new = temp

                temp = []
                for i in range(20):
                    if i == 0:
                        temp.append( delta(acc_y[i],acc_y[i+1],edge=1) * SIGNAL_FACTOR )
                    elif i == 19:
                        temp.append( delta(acc_y[i],acc_y[i-1],edge=1) * SIGNAL_FACTOR )
                    else:
                        temp.append( delta(acc_y[i],acc_y[i-1], acc_y[i+1]) * SIGNAL_FACTOR )
                acc_y_new = temp

                temp = []
                for i in range(20):
                    if i == 0:
                        temp.append( delta(acc_z[i],acc_z[i+1],edge=1) * SIGNAL_FACTOR )
                    elif i == 19:
                        temp.append( delta(acc_z[i],acc_z[i-1],edge=1) * SIGNAL_FACTOR )
                    else:
                        temp.append( delta(acc_z[i],acc_z[i-1], acc_z[i+1]) * SIGNAL_FACTOR )
                acc_z_new = temp

                acc_x = acc_x_new
                acc_y = acc_y_new
                acc_z = acc_z_new

                acc = []
                acc_seq = []
                for j in range (MAX_FRAME):
                    acc_frame = []
                    acc_frame.append(acc_x[j])
                    acc_frame.append(acc_y[j])
                    acc_frame.append(acc_z[j])
                    acc_seq.append(acc_frame)
                acc.append(acc_seq)

                acc = np.array(acc)
                
                # do inference
                prediction = model.predict([video, acc])
                print(prediction)
                if (prediction[0][0] < prediction[0][1]):
                    lapar = True
                else:
                    lapar = False
                    
                if (prediction[0][1] > 0.9):
                    confidence = True
                else:
                    confidence = False
                # result: lapar, confidence
                
                # decision upon inference result
                pull_srv()
                get_input()

                if not(lapar) or reset:
                    break
                else:
                    if confidence:
                        GPIO.output(LED_2, 1)
                        give_feed()
                    else:
                        GPIO.output(LED_2, 0)
                        
    # routine finished
    # turn off LED1 and LED2
    GPIO.output(LED_1, 0)
    GPIO.output(LED_2, 0)
    return
    
def give_stimuli():
    GPIO.output(FEED_CMD, 1)
    time.sleep(STIMULI_TIME_S)
    GPIO.output(FEED_CMD, 0)
    time.sleep(2)
    return
            
def give_feed():
    GPIO.output(FEED_CMD, 1)
    time.sleep(FEED_TIME_S)
    GPIO.output(FEED_CMD, 0)
    time.sleep(2)
    return

def push_srv():

    cur_state_msg = "High Appetite" if cur_state else "Low Appetite"
    if not cur_state:
       confidence_msg = ""
    else:
       confidence_msg = "Likely" if confidence else "Not Likely"
    docs = [
            {"Date": datetime.today().strftime("%x"),
             "Time": datetime.today().strftime("%X"),
             "Status": cur_state_msg,
             "Confidence": confidence_msg,},
           ]
    if not(cur_state == ""):
      result = push_db.insert_many(docs)
    return

def pull_srv():
    global exit_idle, reset
    global exit_idle_web, reset_web

    # pull data from the server
    docs = pull_db.find().sort("_id", -1).limit(1)
    docs_pd = pd.DataFrame(docs)

    exit_idle_web = docs_pd.iloc[0]['Run']
    reset_web = docs_pd.iloc[0]['Reset']

    # make sure there wont be any call queue
    if exit_idle_web or reset_web:
      docs = [
            {"Date": datetime.today().strftime("%x"),
             "Time": datetime.today().strftime("%X"),
             "Reset": 0,
             "Run": 0,},
           ]
      refresh_input = pull_db.insert_many(docs)

    return

def get_input():
    global exit_idle, reset
    global exit_idle_but, exit_idle_web
    global reset_but, reset_web

    exit_idle = exit_idle_but or exit_idle_web
    reset = reset_but or reset_web

    exit_idle_but = 0
    exit_idle_web = 0

    reset_but = 0
    reset_web = 0
    return

# main loop
first_input = [
            {"Date": datetime.today().strftime("%x"),
             "Time": datetime.today().strftime("%X"),
             "Reset": 0,
             "Run": 0,},
           ]
first_input_push = pull_db.insert_many(first_input)

while True:
    cur_state = next_state

    process_loop()
    cur_state = IDLE
    push_srv()

    for i in range(15*60):
      time.sleep(1)
      pull_srv()
      if exit_idle_web:
        break

    if not exit_idle_web:
        pull_srv()
    get_input()
    next_state = get_next_state()
