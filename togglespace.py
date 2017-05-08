#!/usr/bin/python3
import json
from urllib.request import urlopen
import RPi.GPIO as GPIO
import time
import socket
import threading
import os 

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(7, GPIO.OUT)

data = ""

url = ["Status Anzeigen", "Space oeffnen", "Space schliessen"]
with open("/home/pi/spaceOpenCloseButton/token.conf", "r") as token_raw:
    space, token, url_tmp = "","",""
    for line in token_raw.readlines():
        if line[0] == '#':
            pass # Ist ein Kommentar
        else:
            line = line.replace('\n', '')
            key, value = line.split('=')
            if key == 'space':
                space = value
            elif key == 'token':
                token = value
            elif key == 'url':
                url_tmp = value
            elif key == 'listen_IP':
                listen_IP = value
            elif key == 'listen_port':
                listen_port = int(value)
            else:
                pass
    url = [url_tmp + 'space=' + space + '&state=show', url_tmp + 'space=' + space + '&token=' + token + '&state=open', url_tmp + 'space=' + space + '&token=' + token + '&state=closed']
jsonurl = urlopen(url[0])

def rec_UDP():
    global data
    while True:
       	# UDP commands for listening
       	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       	sock.bind((listen_IP, listen_port))
       	data, addr = sock.recvfrom(1024)
       	print("received message:", data)

def do_server_query(action):
	jsonurl = urlopen(url[action])
	jsoncontent = json.loads(bytes.decode(jsonurl.read()))
	return jsoncontent["status"]

currentstatus = do_server_query(0)
print("Startstatus:",currentstatus)

def togglespace():

	jsonurl = urlopen(url[0])
	jsoncontent = json.loads(bytes.decode(jsonurl.read()))
	if jsoncontent["status"] == "open":
		print("see-base is now:", do_server_query(2))
		GPIO.output(11, 1)
		GPIO.output(7, 0)
	elif jsoncontent["status"] == "closed":
		print("see-base is now:", do_server_query(1))
		GPIO.output(7, 1)
		GPIO.output(11, 0)

if do_server_query(0) == "open":
        print("status from server is open")
        GPIO.output(11, 0)
        GPIO.output(7, 1)
        currentstatus = "open"
elif do_server_query(0) == "closed":
        print("status from server is closed")
        GPIO.output(7, 0)
        GPIO.output(11, 1)
        currentstatus = "closed"

try:
	listen_UDP = threading.Thread(target=rec_UDP)
	listen_UDP.start()
	print("Schleife start")
	while True:
		time.sleep(0.1)
		if GPIO.input(15) == GPIO.LOW:
			togglespace()
			time.sleep(0.5)
		if "change" in str(data):
			if do_server_query(0) == "open":
				print("status from server is open")
				GPIO.output(11, 0)
				GPIO.output(7, 1)
			elif do_server_query(0) == "closed":
				print("status from server is closed")
				GPIO.output(7, 0)
				GPIO.output(11, 1)
		data=""
except KeyboardInterrupt:
	print("\nExiting ...\n")
	GPIO.output(11,0)
	GPIO.output(7,0)
	os._exit(0)	
