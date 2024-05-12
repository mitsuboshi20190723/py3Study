#!/usr/bin/env python
# -*- coding: utf-8 -*-


##
 #  2024.5.12
 #  nctplc5555.py
 #  ver.1.0
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##


# -e echo
# -b binary -a ascii


import sys
import socket

file = sys.argv

if len(file) == 1:
	print("Prease input response data : ", end="")
	str = input()
else:
	f = open(file[1], "r")
	str = f.read()
	f.close()


res = bytes.fromhex(str)

print("RESPONSE DATA : " + str)
print("RESPONSE DATA : " + res.hex().upper())

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
				cs.send(res)                                       # for binary
#				print("REQUEST DATA : " + msg.encode("utf-8"))
#				cs.send(str.encode("utf-8"))                       # for ascii


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
