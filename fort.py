#!/usr/bin/env python
# -*- coding: utf-8 -*-


##
 #  2024.10.14
 #  fort.py (False OR True)
 #  ver.0.6
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##



import struct
import datetime
import time
import threading




class read_db(threading.Thread):

	c = [["", ""], ["0", "1"], ["F", "T"]]


	def __init__(self, data_dict):

		super().__init__()
		self.hb = 0


	def heartbeat(self, mode=-2):

		if mode < 0: mode = int(datetime.now().strftime('%S')) % abs(mode)
		else: self.hb += 1 if self.hb < mode else -mode

		return mode


	def fort(self, num, digit=16, mode=0): # e.g. fort(10, mode=0) = 10, fort(0b1010, 4, 1) = "1010", fort(0xA, 4, -2) = "FTFT"

		if mode < -2 or mode == 0 or mode > 2: return num # number

		order = [i for i in range(digit)]
		if mode < 0: mode = -1 * mode # little endian
		else: order = reversed(order) # big endian

		bits = ""
		for i in order:
			n = (num // 2**i) % 2
			bits += read_db.c[mode][n]

		return bits # string


	def run(self):

		a = 255 # "_32bits_"

		try:
			while True:
				try:
					b = self.fort(a, 32, 0)
					c = self.fort(self.heartbeat(), mode=2)

					time.sleep(1.0)

				except:
					traceback.print_exc()
					time.sleep(1.0)

		except KeyboardInterrupt:
			exit(0)




class rorw: # Read OR Write

	def __init__(self):

		self.r = read_db(self.data_dict)


	def start(self):

		self.r.start()




if __name__ == "__main__":

	main = rorw()
	main.start()

	exit(0)




