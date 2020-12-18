#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
 #  2020.11.28
 #  kservo.py
 #  ver 1.0
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
# $ dmesg
# $ sudo sh -c 'echo "ftdi_sio" >> /etc/modules'


from logging import getLogger, config
import serial
import struct
import subprocess
import sys
from time import sleep


config.fileConfig("python_log_config.ini")
logger = getLogger("minimum")


P7500 = [0x81, 0x3A, 0x4C]
P3968 = [0x81, 0x1F, 0x00]


# ./kservo.py

args = sys.argv

try:
	temp = subprocess.Popen("ls -l /dev/ttyUSB0", stdout=subprocess.PIPE, shell=True).communicate()[0]
	s = serial.Serial("/dev/ttyUSB0", 115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE, timeout=1.0)
except Exception as errmsg:
	logger.error("%s", errmsg)
	exit(1)


s.flushOutput()
for i in P7500:
	buff = struct.pack("B", i)
	s.write(buff)

s.flushInput()
msg = s.read(256)
print(type(msg))
logger.warning("%s", bytearray(msg).hex().upper())
logger.warning("%s", list(msg))
logger.warning("%s", msg)
sleep(1)

s.flushOutput()
for i in P3968:
	buff = struct.pack("B", i)
	s.write(buff)

s.flushInput()
msg = s.read(2048)
#print(msg.decode("utf-8"))

sleep(1)

s.flushOutput()
for i in P7500:
	buff = struct.pack("B", i)
	s.write(buff)

s.flushInput()
msg = s.read(2048)
#print(msg.decode("utf-8"))

s.close()
