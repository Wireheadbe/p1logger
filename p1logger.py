#!/usr/bin/python3
# Python script for P1 Telegrams - DSMR5 Fluvius
 
import datetime
import re
import serial
import paho.mqtt.client as paho

# VARIABLES
## broker - define your mqtt broker here
## broker="mqtt.homelab.local"
broker="mqtt.homelab.local"
## port - define the mqtt port
## e.g. port=1883
port=1883
## p1device - define your P1 serial device
## e.g. p1device="/dev/ttyUSB0" - you can typically find these via ls -l /dev/tty*
p1device="/dev/ttyP1"


##  HERE BE DRAGONS ##
## (do not edit :)) ##
def on_publish(client1,userdata,result): #create function for callback
  #print("data published \n")
  pass
 
client1=paho.Client("control1") #create client object
client1.on_publish = on_publish #assign function to callback
client1.connect(broker,port) #establish connection
 
# Serial Port config
ser = serial.Serial()
 
# DSMR 5 Fluvius > 115200 8N1:
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
 
ser.xonxoff = 0
ser.rtscts = 0
ser.timeout = 12
ser.port = p1device
ser.close()
 
client1.loop_start()

# Run indefinitely
while True:
  ser.open()
  checksum_found = False

  # Process below logic until checksum found
  while not checksum_found:
    telegram_line = ser.readline() # Read a line
    telegram_line = telegram_line.decode('utf-8').strip() # Strip spaces and blank lines
 
    #print (telegram_line) #debug
 
    if re.match(r'(?=1-0:1.7.0)', telegram_line): #1-0:1.7.0 = Instantaneous draw in kW
      kwAf = telegram_line[10:-4] # cut kW (0000.54)
      wattAf = float(kwAf) * 1000 # multiply to Watt (540.0)
      wattAf = int(wattAf) # round float (540)
      
    if re.match(r'(?=1-0:2.7.0)', telegram_line): #1-0:2.7.0 = Instantaneous injection in kW
      kwIn = telegram_line[10:-4] # cut kW (0000.54)
      wattIn = float(kwIn) * 1000 # multiply to Watt (540.0)
      wattIn = int(wattIn) # round float (540)
 
    if re.match(r'(?=1-0:1.8.1)', telegram_line): #1-0:1.8.1 - Total Day draw / 1-0:1.8.1(13579.595*kWh)
      kwhAfDag = telegram_line[10:-5] # cut kWh (13579.595)
      kwhAfDag = float(kwhAfDag)
 
    if re.match(r'(?=1-0:1.8.2)', telegram_line): #1-0:1.8.2 - Total Night draw / 1-0:1.8.2(14655.223*kWh)
      kwhAfNacht = telegram_line[10:-5] # cut kWh (14655.223)
      kwhAfNacht = float(kwhAfNacht)
    
    if re.match(r'(?=1-0:2.8.1)', telegram_line): #1-0:1.8.1 - Total Day injection / 1-0:1.8.1(13579.595*kWh)
      kwhInDag = telegram_line[10:-5] # cut kWh (13579.595)
      kwhInDag = float(kwhInDag)
 
    if re.match(r'(?=1-0:2.8.2)', telegram_line): #1-0:1.8.2 - Total Night injection / 1-0:1.8.2(14655.223*kWh)
      kwhInNacht = telegram_line[10:-5] # cut kWh (14655.223)
      kwhInNacht = float(kwhInNacht)

    if re.match(r'(?=0-1:24.2.3\(.+\))', telegram_line): #0-1:24.2.3 - Total gas use m3 / 0-1:24.2.3(200827154000S)(00002.072*m3)
      gasm3 = telegram_line[26:-4] # cut m3 (00002.072)
      gasm3 = float(gasm3)
 
    # Check if checksum received - marks end of telegram
    if re.match(r'(?=!)', telegram_line):
      checksum_found = True
 
  ser.close()
 
######################################
# MQTT PUBLISH
######################################
 
  client1.publish("fluvius/wattAf", wattAf)
  client1.publish("fluvius/wattIn", wattIn)
  client1.publish("fluvius/kwhAfDag", kwhAfDag)
  client1.publish("fluvius/kwhAfNacht", kwhAfNacht)
  client1.publish("fluvius/kwhInDag", kwhInDag)
  client1.publish("fluvius/kwhInNacht", kwhInNacht)
  client1.publish("fluvius/gasm3", gasm3)
  print("Afname: ",wattAf,"| Injection: ",wattIn)

client1.disconnect()
