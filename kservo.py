#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
 #  2023.11.12
 #  kservo.py
 #  ver.2.0
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##


# $ lsusb
# $ lsmod | grep ftdi
# $ sudo su
# # modprobe ftdi-sio
# # echo 165C 0008 > /sys/bus/usb-serial/drivers/ftdi_sio/new_id
# # ls -l /dev/ttyUSB*
# # chmod o+rw /dev/ttyUSB0
# # exit
# $ cat /sys/bus/usb-serial/drivers/ftdi_sio/new_id
# $ lsmod | grep ftdi
# $ sudo dmesg
# $ sudo sh -c 'echo "ftdi_sio" >> /etc/modules'


import serial
import struct
import subprocess
import sys
from time import sleep


GET_ID = [0xFF, 0x00, 0x00, 0x00] # get ID -> 0-31
SET_ID_ZERO = [0xE0, 0x01, 0x01, 0x01]
SET_ID = [0xEF, 0x01, 0x01, 0x01] # set ID=15(239%32)
P7500 = [0x83, 0x3A, 0x4C] # move ID=3 P=7500(58*128+76)
P3968 = [0x83, 0x1F, 0x00]


# ./kservo.py

args = sys.argv

try:
	temp = subprocess.Popen("ls -l /dev/ttyUSB0", stdout=subprocess.PIPE, shell=True).communicate()[0]
	s = serial.Serial("/dev/ttyUSB0", 115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE, timeout=1.0)
except Exception as errmsg:
	print(errmsg)
	exit(1)

# print(type(GET_ID))
# print(list(GET_ID))

s.flushOutput()
print(bytearray(P7500).hex().upper())

for i in P7500:
	request = struct.pack("B", i)
	s.write(request)

s.flushInput()
response = s.read(256)
print(bytearray(response).hex().upper())


sleep(1)


s.flushOutput()
for i in P3968:
	buff = struct.pack("B", i)
	s.write(buff)

s.flushInput()
msg = s.read(2048)
print(bytearray(msg).hex().upper())


sleep(1)


s.flushOutput()
for i in P7500:
	buff = struct.pack("B", i)
	s.write(buff)

s.flushInput()
msg = s.read(2048)
print(bytearray(msg).hex().upper())

s.close()
