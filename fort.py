#!/usr/bin/env python
# -*- coding: utf-8 -*-


##
 #  2024.10.10
 #  fort.py (False OR True)
 #  ver.0.5
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##



import time
import threading
import struct



def torf(num, digit=16, mode=0): # e.g. torf(10, mode=0) = 10, torf(0b1010, 4, -1) = "1010", torf(0xA, 4, 2) = "FTFT"

	if mode < -2 or mode == 0 or mode > 2: return num # number

	c = [["", ""], ["0", "1"], ["F", "T"]]

	order = [i for i in range(digit)]
	if mode < 0:                                  # lambda
		order = reversed(order)
		mode *= -1

	bits = ""
	for i in order:                                 # lambda
		n = (num // 2**i) % 2
		bits += c[mode][n]

	return bits # string



"""

000100020003000400050006000700080009000A big endian

\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06\x00\x07\x00\x08\x00\x09\x00\x0A\x00 little endian


"""


class read_db(threading.Thread):

	c = [["", ""], ["0", "1"], ["F", "T"]]


	def __init__(self, data_dict):

		super().__init__()
		self.hb = 0


	def heartbeat(self, mode=-1):

		if mode < 0:
			strsec = datetime.now().strftime('%S')
			mode = int(strsec) # // 2

		return mode


	def torf(self, num, digit=16, mode=0): # e.g. torf(10, mode=0) = 10, torf(0b1010, 4, -1) = "1010", torf(0xA, 4, 2) = "FTFT"

		if mode < -2 or mode == 0 or mode > 2: return num # number

		order = [i for i in range(digit)]
		if mode < 0:
			order = reversed(order)
			mode *= -1

		bits = ""
		for i in order:
			n = (num // 2**i) % 2
			bits += read_db.c[mode][n]

		return bits # string


	def run(self):

		a = 255 # "_16bits_"

		try:
			while True:
				try:
					b = torf(self.data_dict[i][0], mode=0)

					c = self.torf(self.heartbeat(), mode=2)
					d = self.heartbeat()

					time.sleep(1.0)

				except:
					traceback.print_exc()
					time.sleep(1.0)

		except KeyboardInterrupt:
			exit(0)




class rorw:

	def __init__(self):

		self.r = read_db(self.data_dict)


	def start(self):

		self.r.start()




if __name__ == "__main__":

	main = rorw()
	main.start()

	exit(0)




