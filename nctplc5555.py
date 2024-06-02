#!/usr/bin/env python
# -*- coding: utf-8 -*-


##
 #  2024.6.2
 #  nctplc5555.py
 #  ver.1.5
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##


# e.g.  ./nctplc5555.py -b
#       ./nctplc5555.py -a foo.res


import sys
import socket


file = sys.argv

input_file = 0
msg_type = 0
for c in range(len(file)):
	if file[c][0] == "-":
		if   file[c][1] == "a": # ascii
			msg_type = 0
		elif file[c][1] == "b": # binary
			msg_type = 1
		elif file[c][1] == "e": # echo
			response = "echo"
	elif ".res" in file[c]:
		input_file = 1
		with open(file[c], "r") as f:
			response = f.read()

if not input_file:
	print("Prease input response data : ", end="")
	response = input()




print("RESPONSE DATA : " + response)

res = bytes.fromhex(response)
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

				elif msg_type == 0:
					print("REQUEST DATA : " + msg.encode("utf-8"))
					if response == "echo":
						response = msg.encode("utf-8")
					cs.send(response.encode("utf-8"))

				elif msg_type == 1:
					if response == "echo":
						response = msg
					print("REQUEST DATA : " + msg.hex().upper())
					cs.send(response)



#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind(("127.0.0.1", 5555))
#s.listen(1)

#str = "RESPNSE DATA"
#while True:
#	cs, addr = s.accept()
#	print("Connection from ", addr)
#	msg = cs.recv(4096).decode("utf-8")
#	print("REQUEST DATA : " + msg)
#	cs.send(bytes(str, 'utf-8'))
#	cs.close()

#s.close()
