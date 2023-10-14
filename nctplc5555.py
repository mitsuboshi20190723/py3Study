#!/usr/bin/env python
# -*- coding: utf-8 -*-


##
 #  2023.10.14
 #  nctplc5555.py
 #  ver.1.0
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##


# echo
# -b bynary -a ascii


import sys
import socket



res = b'\xD0\x00\x00\xFF\xFF\x03\x00\x8A\x00\x00\x00\x16\x00\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06\x00\x07\x00\x08\x00\x09\x00\x0A\x00\x0B\x00\x0C\x00\x0D\x00\x0E\x00\x0F\x00\x10\x00\x11\x00\x12\x00\x13\x00\x14\x00\x15\x00\x16\xAA\x17\xAA\x18\xAA\x19\xAA\x1A\xAA\x1B\xAA\x1C\xAA\x1D\xAA\x1E\xAA\x1F\xAA\x16\x00\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06\x00\x07\x00\x08\x00\x09\x00\x0A\x00\x0B\x00\x0C\x00\x0D\x00\x0E\x00\x0F\x00\x10\x00\x11\x00\x12\x00\x13\x00\x14\x00\x15\x00\xE7\x07\x0A\x00\x0F\x00\x0C\x00\x22\x00\x38\x00\x1C\xAA\x1D\xAA\x1E\xAA\x1F\xAA\xFF\xFF\x00\x00\xFF\xFF\x00\x00'


 
file = sys.argv

if len(file) == 1:
	print("Prease input response data :")
	str = input()
else:
	f = open(file[1], "r")
	str = f.read()
	f.close()

print("RESPONSE DATA : " + str)
print("RESPONSE DATA : " + res.hex())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.bind(("127.0.0.1", 5555))
	s.listen(1)

	while True:
		cs, addr = s.accept()
		print("Connection from ", addr)
		with cs:
			while True:
				msg = cs.recv(4096)
				if not msg:
					break
				print("REQUEST DATA : " + msg.hex().upper())
				cs.send(res)
#				print("REQUEST DATA : " + msg.encode("utf-8"))
#				cs.send(str.encode("utf-8"))


#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind(("127.0.0.1", 5555))
#s.listen(1)

#while True:
#	cs, addr = s.accept()
#	print("Connection from ", addr)
#	msg = cs.recv(4096).decode("utf-8")
#	print("REQUEST DATA : " + msg)
#	cs.send(bytes(str, 'utf-8'))
#	cs.close()

#s.close()
