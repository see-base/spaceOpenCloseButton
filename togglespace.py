#!/usr/bin/python3
import json
from urllib.request import urlopen
import RPi.GPIO as GPIO
import time
import socket
import threading

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)

data = ""

url = ["https://bodensee.space/cgi-bin/togglestate?space=see-base&state=show", "(token url zum öffnen einfügen)", "token url zum schließen einfügen", "syntax unbekannt und nicht Dokumentiert"]
jsonurl = urlopen(url[0])

def rec_UDP():
    global data
    while True:
        # UDP commands for listening
        UDP_PORT = 5000
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('94.45.232.224', UDP_PORT))
        data, addr = sock.recvfrom(1024)
        print("received message:", data)

def do_server_query(action):
	jsonurl = urlopen(url[action])
	jsoncontent = json.loads(bytes.decode(jsonurl.read()))
	return jsoncontent["status"]

startstatus = do_server_query(0)
print("Startstatus:",startstatus)

def togglespace():

	jsonurl = urlopen(url[0])
	jsoncontent = json.loads(bytes.decode(jsonurl.read()))
	if jsoncontent["status"] == "open":
		print("see-base is now:", do_server_query(2))
		GPIO.output(11, 1)
		GPIO.output(8, 0)
	elif jsoncontent["status"] == "closed":
		print("see-base is now:", do_server_query(1))
		GPIO.output(8, 1)
		GPIO.output(11, 0)


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
			GPIO.output(8, 1)
		elif do_server_query(0) == "closed":
			print("status from server is closed")
			GPIO.output(8, 0)
			GPIO.output(11, 1)
	data=""

GPIO.output(11,0)
GPIO.output(8,0)
