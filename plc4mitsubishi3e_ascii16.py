#!/usr/bin/env python
# -*- coding: utf-8 -*-


##
 #  2020.12.28
 #  plc4mitsubishi3e_ascii16.py
 #  ver 1.0
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##


from logging import getLogger, config
import socket
from time import sleep
import numpy as np
import datetime
import struct
import binascii

config.fileConfig("python_log_config.ini")
logger = getLogger("develop")

response_head = 22

# support devices
# word = W*, SD
# bit  = B*, SM


class Device:
	def __init__(self, code="", addr="", size="", data=""):
		self.code = code
		self.addr = addr
		self.size = size
		self.data = data


	def str(self):
		return self.code + self.addr + self.size + self.data


	def set_dev(self, code, addr, size="", data=""):
		self.code = d1
		self.addr = d2
		self.size = d3
		self.data = d4
		return self.str()


class Mitsubishi3E:

	BUFF_SIZE = 4096

	def __init__(self):
		self.sub_h      = "0000"
		self.net_num    = "00"
		self.pc_num     = "00"
		self.unit_io    = "0000"
		self.unit_ch    = "00"

		self.nlen       = "0000"

		self.cputimer   = "0000"
		self.command    = "0000"
		self.subcommand = "0000"

		self.devices    = "**0000000000"

		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except OSError as errmsg:
			logger.error("%s", errmsg)
			exit(1)


	def join_msg(self):
		msg  = self.sub_h + self.net_num + self.pc_num + self.unit_io + self.unit_ch
		msg += self.nlen
		msg += self.cputimer + self.command + self.subcommand
		msg += self.devices
		return msg


	def set_plc(self, sub_h="5000", net_num="00", pc_num="FF", unit_io="03FF", unit_ch="00"):
		self.sub_h   = sub_h
		self.net_num = net_num
		self.pc_num  = pc_num
		self.unit_io = unit_io
		self.unit_ch = unit_ch


	def set_cputimer(self, cputimer="0004"):
		self.cputimer = cputimer # 1.0 sec


	def set_command(self, command, subcommand):
		self.command    = command
		self.subcommand = subcommand


	def connect(self, addr, port, sec=1):
		try:
			self.s.settimeout(sec)
			self.s.connect((addr, int(port)))
		except OSError as errmsg:
			self.s.close()
			logger.error("Cannot connect PLC (%s)", errmsg)
			exit(1)


	def close(self): # disconnect PLC
		self.s.close()


	def connect2(self, sub_h, net_num, pc_num, unit_io, unit_ch, addr, port):
		set_plc(self, sub_h, net_num, pc_num, unit_io, unit_ch)
		connect(self, addr, port)


	def get_system_clock(self):
		b = Device("SM", "000213", data="01")
		self.write_random(b, 0)

		w = Device("SD", "000210", "0007")
		res = self.read_batch(w)
		res = res[response_head:]
		dt = [0,0,0,0,0,0]
		for i in dt:
			dt[i] = m2i(res, offset=i)

		return datetime.datetime(dt[0], dt[1], dt[2], dt[3], dt[4], dt[5], dt[6])


	def backup(self):
		w = Device("SD", "009350", data="0000")
		self.write_random(w, 1)

		w = Device("SD", "009351", data="0001")
		self.write_random(w, 1)

		b = Device("SM", "001351", data="01")
		self.write_random(b, 0)

		sleep(1)

		err_code = "success"
		b = Device("SM", "000953")
		res = self.read_random(b, 0)
		print("SM953 : " + split_response(res))
		if int(res[-4:]) & 1 == 1:
			w = Device("SD", "000953")
			err_code = self.read_random(w, 1)

		return err_code


	def restore(self, restore_file="122920200009"):#"122920200009"

		w = Device("SD", "000954", data="0000") # all data
		self.write_random(w, 1)

		if len(restore_file) == 0:
			w = Device("SD", "000955", data="1000") # bit13 -> ON
			self.write_random(w, 1)
		else:
			file = Device("SD", "000956", "0003", restore_file) # 2020.12.2 00015 -> "12022020000F"
			self.write_batch(file)

		w = Device("SD", "009351", data="0001")
		self.write_random(w, 1)

		sleep(1)

		b = Device("SM", "001354", data="01")
		self.write_random(b, 0)

		sleep(5)

		err_code = "success"
		b = Device("SM", "000959")
		res = self.read_random(b, 0)
		print("SM959 : " + split_response(res))
		if int(res[-4:]) & 1 == 1:
			w = Device("SD", "000959")
			err_code = self.read_random(w, 1)
		print("SD959 : " + split_response(self.read_random(Device("SD", "000959"), 1)))
		return err_code


	def read(self, *dev):
		pass


	def read_batch(self, dev, bwd=1):
		self.set_command("0401", "0000" if bwd != 0 else "0001")
		self.devices = dev.str()
		self.nlen = format(12+len(self.devices), "04X") # 12 = 4 + 4 + 4
		return self.snr(self.join_msg())


	def read_random(self, dev, bwd=1): # n=1
		self.set_command("0403", "0000")
		if bwd < 2:
			self.devices = "0100"
		else:
			self.devices = "0001"

		self.devices += dev.str()

		self.nlen = format(12+len(self.devices), "04X") # 12 = 4 + 4 + 4

		return self.snr(self.join_msg())


	def read_block(self, wdev, bdev):
		self.set_command("0406", "0000")
		self.devices = format(len(wdev), "02X") + format(len(bdev), "02X")
		for i in range(len(wdev)):
			self.devices += wdev[i].str()
		for i in range(len(bdev)):
			self.devices += bdev[i].str()

		self.nlen = format(12+len(self.devices), "04X") # 12 = 4 + 4 + 4
		return self.snr(self.join_msg())


	def write(self, *dev):
		pass


	def write_batch(self, dev, bwd=1):
		self.set_command("1401", "0000" if bwd != 0 else "0001")
		self.devices = dev.str()
		self.nlen = format(12+len(self.devices), "04X") # 12 = 4 + 4 + 4
		return self.snr(self.join_msg(), -1)


	def write_random(self, dev, bwd=1): # n=1
		self.set_command("1402", "0000" if bwd != 0 else "0001")
		if   bwd == 0:
			self.devices = "01" + dev.str()
		elif bwd == 1:
			self.devices = "0100" + dev.str()
		elif bwd == 2:
			self.devices = "0001" + dev.str()
		self.nlen = format(12+len(self.devices), "04X") # 12 = 4 + 4 + 4
		return self.snr(self.join_msg(), -1)
		

	def write_block(self, wdev, bdev):
		self.set_command("1406", "0000")
		self.devices = format(len(wdev), "02X") + format(len(bdev), "02X")
		for i in range(len(wdev)):
			self.devices += wdev[i].str()
		for i in range(len(bdev)):
			self.devices += bdev[i].str()		

		self.nlen = format(12+len(self.devices), "04X") # 12 = 4 + 4 + 4
		return self.snr(self.join_msg())


	def remote(self, str):
		
		if   str == "RUN":
			self.set_command("1001", "0000")
			self.devices = "00010000" # soft run only
		elif str == "STOP":
			self.set_command("1002", "0000")
			self.devices = "0000"
		elif str == "PAUSE":
			self.set_command("1003", "0000")
			self.devices = "0001" # soft pause only
		elif str == "LC":
			self.set_command("1005", "0000")
			self.devices = "0000"
		elif str == "RESET":
			self.set_command("1006", "0000")
			self.devices = "0000"
		elif str == "TEST":
			self.set_command("0619", "0000")
			self.devices = ""
		else:
			return "Cannot find " + str

		self.nlen = format(12+len(self.devices), "04X") # 12 = 4 + 4 + 4
		return self.snr(self.join_msg())


	def password(self): # LOCK UNLOCK
		pass


	def snr(self, request, t=0.25):
		try:
			self.s.send(request.encode("utf-8"))
			if t < 0:
				return "SENDED"
			sleep(t)
			response = self.s.recv(Mitsubishi3E.BUFF_SIZE).decode("utf-8")
		except OSError as errmsg:
			logger.error("%s", errmsg)
			sleep(0.25)
			return "NORESPONSE"

		if len(response) == 0:
			return "NORESPONSE"
		return response



def set16(d, n=0):
	d = d | 1 << 15-n%16
	return d

def reset16(d, n=0):
	d = d & ~(1 << 15-n%16) # ~(-d -1 | 1 << 15-n%16)
	return d


def m2b(s, offset=0): # msg16 -> int64
	s16 = s[offset//16:offset//16+4]
	return int(s16, 16) >> offset%16 & 0b1

def m2c(s, offset=0): # msg16 -> int64
	s4 = s[offset:offset+1]
	return int(s4)

def m2i(s, sgn="-", offset=0): # msg16 -> int64
	s16 = s[offset*4:offset*4+4]
	return int(str(np.array(int(s16, 16), dtype=np.int16))) # dtype=np.uint16

def m2d(s, sgn="-", offset=0): # msg16 -> int64
	s32 = s[offset*4:offset*4+8]
	return int(str(np.array(int(s32, 16), dtype=np.int32))) # dtype=np.uint32

def m2f(s, offset=0): # msg32 -> float64
	s32 = s[offset*4+4:offset*4+8] + s[offset*4:offset*4+4]
	return struct.unpack('>f', binascii.unhexlify(s32))[0]



def i2m(d, sgn="-"): # int -> msg16
	if sgn != "u" and sgn != "U":
		d += 65536 * (d<0)
	return format(d, "04X")

def d2m(d, sgn="-"): # int -> msg32
	if sgn != "u" and sgn != "U":
		d += 4294967296 * (d<0)
	return format(d, "08X")

def f2m(r): # float -> msg32
	s = hex(struct.unpack('>I', struct.pack('>f', r))[0]).upper()
	return  s[6:10] + s[2:6]


def choice_from_response(req, res, dev):
	pass

def split_response(res):
	p = response_head
	str =  res[:p-4]
	str += " " + res[p-4:p] + "\n" # error code
	while p + 4 < len(res):
		str += res[p:p+4] + " "
		p += 4
	return str + res[p:]

def N():
	return np.array([], dtype=np.int16)

def M(L):
	return np.array(L, dtype=np.int16)

if __name__ == "__main__":
	logger.info("Test functions")
##	for i in range(16):
##		print(i2m(set16(0, i)))
##	for i in range(16):
##		print(i2m(reset16(65535, i)))
	s = input("Prease input number : ")
	t = input("Number is float or int ? [f/i] : ")
	if t == "f":
		n = float(s)
		print(f2m(n) + " (IEEE754 : " + f2m(n)[-4:] + f2m(n)[:4] + ") -> " + str((m2f(f2m(n)))))
	else:
		n = int(s)
		b = input("Number is 16bit or 32bit ? [16/32] : ")
		u = input("Number is unsigned or signed ? [u/s] : ")
		if   b == "16" and u == "s": #           -32,768 - 32,767
			print( i2m(n) + " -> " + str(m2i(i2m(n))) )
		elif b == "16" and u == "u": #                 0 - 65,535
			print( i2m(n, u) + " -> " + str(m2i(i2m(n, u))) )
		elif b == "32" and u == "s": #    -2,147,483,648 - 2,147,483,647
			print( d2m(n) + " -> " + str(m2d(d2m(n))) )
		elif b == "32" and u == "u": #                 0 - 4,294,967,295
			print( d2m(n, u) + " -> " + str(m2d(d2m(n, u))) )
