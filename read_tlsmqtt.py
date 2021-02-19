#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
 #  2021.2.18
 #  read_tlsmqtt.py
 #  ver 0.1
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##

import sys
from time import sleep
#import json
import datetime
import paho.mqtt.client as mqtt


# ex  : $ ./read_tlsmqtt.py localhost 1883 topic

args = sys.argv

addr = args[1]
port = args[2]
topic = args[3]


def on_connect(client, userdata, flag, rc):
	print("Connected with result code " + str(rc))
	client.subscribe(topic)

def on_disconnect(client, userdata, flag, rc):
	if rc != 0:
	print("Unexpected disconnection.")

def on_message(client, userdata, msg):
	print(msg.topic + " " + str(msg.payload))

	timestamp = datetime.datetime.today()
	file_name = "./json_data/" + timestamp.strftime("%Y%m%d_%H%M%S_") + "mqtt.json"

	try:
		jf = open(file_name, "w")
	except OSError as errmsg:
		print(errmsg)
	else:
		jf.write(str(msg.payload))
		jf.close()

	print("Prease type command  : $ cat " + file_name + " | jq")


client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
#client.tls_set("~/ca.crt")
#client.connect(192.168.73.163, 8883)
client.connect("localhost", 1883, 60)

client.loop_forever()

