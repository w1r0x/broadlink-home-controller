#!/usr/bin/python

import broadlink
import time
import json
import serial
import binascii
import sys
import random

config_file_name = '/etc/broadlink_buttons.json'

with open(config_file_name, 'r') as buttons_file:    
  buttons = json.load(buttons_file) 

print('Prepairing device...')

devices = broadlink.discover(timeout=2)

rm3 = devices[0]
rm3.auth()

print('Ready!')

def learning_mode():
  button_name = input('Enter button name:')

  while True:
    try:
      rm3.enter_learning()

      ir_packet = None
      while ir_packet == None:
        ir_packet = devices[0].check_data()
        time.sleep(0.1)

      ir_packet = binascii.hexlify(ir_packet).decode('ascii')
      print(ir_packet)
      try:
        buttons[button_name].append(ir_packet)
      except KeyError:
        buttons[button_name] = [ir_packet]
    except KeyboardInterrupt:
      print(buttons[button_name])
      break

  with open(config_file_name, 'w') as buttons_file:    
    json.dump(buttons, buttons_file) 

  sys.exit(0)

def push(button_name):
  time.sleep(0.2)
  try:
    code = random.choice(buttons[button_name])
  except KeyError:
    print('Not found')
  
  rm3.send_data(binascii.unhexlify(code))

def switch_tv_input():
  for i in range(2):
    push("LG Input")
  push("LG OK")

def switch_audio_input():
  global audio_state
  if audio_state == 0:
    for i in range(3):
      push("Logitech Input")
      audio_state += 1
  elif audio_state == 3:
    push("Logitech Input")
    audio_state += 1
  elif audio_state == 4:
    for i in range(2):
      push("Logitech Input")
      audio_state = 0

def press_space():
  bashCommand = ['xte','keydown space','keyup space']
  import subprocess
  process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
  output, error = process.communicate()

def reboot_to_win():
  bashCommand = ['/usr/local/bin/reboot_to_win']
  import subprocess
  process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
  output, error = process.communicate()

def press_left():
  bashCommand = ['xte', 'key Left']
  import subprocess
  process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
  output, error = process.communicate()

def press_right():
  bashCommand = ['xte', 'key Right']
  import subprocess
  process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
  output, error = process.communicate()



def power_switch():
  push("Logitech Power On")
  push("LG Power Switch")

# main loop

#learning_mode()

audio_state = 0

repeatable = ['20DFC639','20DF8679']
white_list = ['20DF8E71', '20DF4EB1', '20DFC639', '20DF8679', '20DF14EB', '20DFDA25', '20DF0DF2', '20DF8D72', '20DF8976', '20DFF10E', '20DF718E']

ser = serial.Serial('/dev/ttyUSB0', 9600)
old_data = ''

ignore = [] 

while True:
  data = ser.readline().strip().decode('utf-8')

  if (data not in white_list): continue
 
  print('old_data: {}, data: {}'.format(old_data, data))

  #Repeat
  if ( data == 'FFFFFFFF' ):
    print('repeat') 
    if ( old_data in repeatable ):
      data = old_data

  old_data = data

  #time.sleep(0.2)

  #Codes
  if ( data == '20DF8E71' ):
    print("Switching Audio Input")
    switch_audio_input()
  elif ( data == '20DF4EB1' ):
    print("Powering Logitech")
    push("Logitech Power On")
  elif ( data == '20DFC639' ):
    print("Logitech Volume Down")
    push("Logitech Volume Down")
  elif ( data == '20DF8679' ):
    print("Logitech Volume Up")
    push("Logitech Volume Up")
  elif ( data == '20DF14EB' ):
    print("Switch TV Input")
    switch_tv_input()
  elif ( data == '20DFDA25' ):
    print("Logitech Input")
    push("Logitech Input")
  elif ( data == '20DF0DF2' ):
    print("Press Space")
    press_space()
  elif ( data == '20DF8D72' ):
    print('Power switch')
    power_switch()
  elif ( data == '20DF8976' ):
    print('Rebooting to win')
    reboot_to_win()
  elif ( data == '20DFF10E' ):
    print('Pressing Left')
    press_left()
  elif ( data == '20DF718E' ):
    print('Pressing Right')
    press_right()


#while True:
#  switch_audio_input()
#  time.sleep(2)



#  button_name = input('What to push? : ')
#  push(button_name)


#switch_tv_input()
