#!/usr/bin/env python
# -*- coding: utf-8 -*-


##
 #  2021.2.18
 #  plc4mitsubishi3e.py
 #  ver 1.2
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##


from logging import getLogger, config
import socket
#import pickle
from time import sleep
import numpy as np
import datetime
import struct
#import binascii

config.fileConfig("python_log_config.ini")
logger = getLogger("develop")

request_head = 11
response_head = 11


msg8 = np.uint8
np.set_printoptions(formatter = {"int": "{:02X}".format})


# support devices
swd = {"W*": 0xB4, "SD": 0xA9} # support_word_devices
sbd = {"B*": 0xA0, "SM": 0x91} # support_bit_devices


def N():
	return np.array([], dtype=msg8)


def M(L):
	return np.array([L], dtype=msg8)


def format_msg(integer, n):
	msg = np.zeros(n, dtype=msg8)

	for i in range(n):
		integer, remainder = divmod(integer, 0x100)
		msg[i] = remainder
		if integer == 0: break
#		print(integer, remainder)
	if integer > 0:
		print("WERNING")

	return msg


def a2b(str): # ascii to binary8
	msg = N()

	for i in range(len(str)//2):
		if str[:2].isnumeric():
			msg = np.append(msg, int(str[:2], 16))
		elif str[:2] in swd:
			d = swd.get(str[:2])
			msg = np.append(msg, d)
		elif str[:2] in sbd:
			d = sbd.get(str[:2])
			msg = np.append(msg, d)
		else:
			return N()

		str = str[2:]

	return msg




class Device:
	def __init__(self, addr=N(), code=N(), size=N(), data=N()):
		self.addr = addr
		self.code = code
		self.size = size
		self.data = data


	def join_msg(self):
		msg = self.addr
		msg = np.append(msg, self.code)
		msg = np.append(msg, self.size)
		msg = np.append(msg, self.data)

		return msg


	def set_dev(self, addr, code, size=N(), data=N()):
		flag = 0
		self.addr = addr.astype(msg8)
		if len(self.addr) != 3: flag = 1
		self.code = code.astype(msg8)
		if len(self.code) != 1: flag = 1
		self.size = size
		self.data = data

		if flag == 1:
			return N()
		else:
			return self.join_msg()



class Mitsubishi3E:

	BUFF_SIZE = 4096

	def __init__(self):
		self.sub_h      = np.zeros(2, dtype=msg8)
		self.net_num    = np.zeros(1, dtype=msg8)
		self.pc_num     = np.zeros(1, dtype=msg8)
		self.unit_io    = np.zeros(2, dtype=msg8)
		self.unit_ch    = np.zeros(1, dtype=msg8)

		self.nlen       = np.zeros(2, dtype=msg8)

		self.cputimer   = np.zeros(2, dtype=msg8)
		self.command    = np.zeros(2, dtype=msg8)
		self.subcommand = np.zeros(2, dtype=msg8)

		self.devices    = N()

		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except OSError as errmsg:
			logger.error("%s", errmsg)
			exit(1)


	def join_msg(self):
		msg = self.sub_h
		msg = np.append(msg, self.net_num)
		msg = np.append(msg, self.pc_num)
		msg = np.append(msg, self.unit_io)
		msg = np.append(msg, self.unit_ch)

		msg = np.append(msg, self.nlen)

		msg = np.append(msg, self.cputimer)
		msg = np.append(msg, self.command)
		msg = np.append(msg, self.subcommand)

		msg = np.append(msg, self.devices)
		return msg


	# def set_plc(self, sub_h=a2b("5000"), net_num=a2b("00"), pc_num=a2b("FF"), unit_io=a2b("03FF"), unit_ch=a2b("00")): ########## "FF03"
	def set_plc(self, sub_h=M([0x50,0x00]), net_num=M([0x00]), pc_num=M([0xFF]), unit_io=M([0xFF, 0x03]), unit_ch=M([0x00])):
		self.sub_h   = sub_h
		self.net_num = net_num
		self.pc_num  = pc_num
		self.unit_io = unit_io
		self.unit_ch = unit_ch


	def set_cputimer(self, cputimer=format_msg(4, 2)):
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


	def get_system_clock(self): ##############################
		b = Device("SM", "000213", data="01")
		self.write_random(b, 0)

		w = Device("SD", "000210", "0007")
		res = self.read_batch(w)
		res = res[response_head:]
		dt = [0,0,0,0,0,0]
		for i in dt:
			dt[i] = m2i(res, offset=i)

		return datetime.datetime(dt[0], dt[1], dt[2], dt[3], dt[4], dt[5], dt[6])


	def backup(self): ################
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


	def restore(self, restore_file="122920200009"):#"122920200009"#######################

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
		self.set_command(np.array([0x01,0x04]), np.array([0x00,0x00]) if bwd != 0 else np.array([0x01,0x00]))
		self.devices = dev.join_msg()
		self.nlen = format_msg(6+len(self.devices), 2) # 6 = 2 + 2 + 2
		return self.snr(self.join_msg())


	def read_random(self, dev, bwd=1): # n=1
		self.set_command(np.array([0x03,0x04]), np.array([0x00,0x00]))
		if bwd < 2:
			self.devices = np.array([0x01,0x00])
		else:
			self.devices = np.array([0x00,0x01])

		self.devices += dev.join_msg()
		self.nlen = format_msg(6+len(self.devices), 2) # 6 = 2 + 2 + 2
		return self.snr(self.join_msg())


	def read_block(self, wdev, bdev):
		self.set_command(np.array([0x06,0x04]), np.array([0x00,0x00]))
		self.devices = format_msg(len(wdev), 1)
		self.devices = np.append(self.devices, format_msg(len(bdev), 1))
		for i in range(len(wdev)):
			self.devices = np.append(self.devices, wdev[i].join_msg())
		for i in range(len(bdev)):
			self.devices = np.append(self.devices, bdev[i].join_msg())

		self.nlen = format_msg(6+len(self.devices), 2) # 6 = 2 + 2 + 2
		return self.snr(self.join_msg())


	def write(self, *dev):
		pass


	def write_batch(self, dev, bwd=1):
		self.set_command(np.array([0x01,0x14]), np.array([0x00,0x00]) if bwd != 0 else np.array([0x01,0x00]))
		self.devices = dev.join_msg()
		self.nlen = format_msg(6+len(self.devices), 2) # 6 = 2 + 2 + 2
		return self.snr(self.join_msg(), -1)


	def write_random(self, dev, bwd=1): # n=1
		self.set_command(np.array([0x02,0x14]), np.array([0x00,0x00]) if bwd != 0 else np.array([0x01,0x00]))
		if   bwd == 0:
			self.devices = np.array([0x01])
			self.devices = np.append(self.devices, dev.join_msg())
		elif bwd == 1:
			self.devices = np.array([0x01,0x00])
			self.devices = np.append(self.devices, dev.join_msg())
		elif bwd == 2:
			self.devices = np.array([0x00,0x01])
			self.devices = np.append(self.devices, dev.join_msg())
		self.nlen = format_msg(6+len(self.devices), 2) # 6 = 2 + 2 + 2
		return self.snr(self.join_msg(), -1)
		

	def write_block(self, wdev, bdev):
		self.set_command(np.array([0x06,0x14]), np.array([0x00,0x00]))
		self.devices = format_msg(len(wdev), 1)
		self.devices = np.append(self.devices, format_msg(len(bdev), 1))
		for i in range(len(wdev)):
			self.devices = np.append(self.devices, wdev[i].join_msg())
		for i in range(len(bdev)):
			self.devices = np.append(self.devices, bdev[i].join_msg())		

		self.nlen = format_msg(6+len(self.devices), 2) # 6 = 2 + 2 + 2
		return self.snr(self.join_msg(), -1)


	def remote(self, str):
		
		if   str == "RUN":
			self.set_command(np.array([0x01,0x10]), np.array([0x00,0x00]))
			self.devices = np.array([0x01,0x00,0x00,0x00]) # soft run only
		elif str == "STOP":
			self.set_command(np.array([0x02,0x10]), np.array([0x00,0x00]))
			self.devices = np.array([0x00,0x00])
		elif str == "PAUSE":
			self.set_command(np.array([0x03,0x10]), np.array([0x00,0x00]))
			self.devices = np.array([0x01,0x00]) # soft pause only
		elif str == "LC":
			self.set_command(np.array([0x05,0x10]), np.array([0x00,0x00]))
			self.devices = np.array([0x00,0x00])
		elif str == "RESET":
			self.set_command(np.array([0x06,0x10]), np.array([0x00,0x00]))
			self.devices = np.array([0x00,0x00])
		elif str == "TEST":
			self.set_command(np.array([0x19,0x06]), np.array([0x00,0x00]))
			self.devices = np.array([], dtype=msg16)################ response ari
		else:
			return "Cannot find " + str

		self.nlen = format_msg(6+len(self.devices), 2) # 6 = 2 + 2 + 2
		return self.snr(self.join_msg(), -1)


	def password(self): # LOCK UNLOCK
		pass


	def snr(self, request, t=0.25):
		try:
			# logger.info(request)
			# logger.info(request.astype(np.uint8).tobytes().hex())
			self.s.send(request.astype(np.uint8).tobytes())
			# self.s.send(request.encode("utf-8"))

			if t < 0:
				return "SENDED"

			sleep(t)

			response = np.frombuffer(self.s.recv(Mitsubishi3E.BUFF_SIZE), dtype=msg8)
			# response = self.s.recv(Mitsubishi3E.BUFF_SIZE).decode("utf-8")

#			full_msg = b''
#			while True:
#				msg = self.s.recv(Mitsubishi3E.BUFF_SIZE)
#				if len(msg) <= 0:
#					break
#				full_msg += msg
#			response = np.frombuffer(full_msg, dtype=msg8)
#			logger.info(full_msg.hex())

		except OSError as errmsg:
			logger.error("%s", errmsg)
			sleep(0.25)
			return N()

		if len(response) == 0:
			return N()
		return response

# >f big endian
# <f little endian

def set16(d, n=0):
	d = d | 1 << 15-n%16
	return d

def reset16(d, n=0):
	d = d & ~(1 << 15-n%16) # ~(-d -1 | 1 << 15-n%16)
	return d


def m2b(m, offset=0): # msg16 -> int64
	m16 = m[(offset//16)*2+1] * 256 + m[(offset//16)*2]
	b = np.array(m16, dtype=np.uint16)
#	print("In m2b:ofset=" + str(offset) +", data="+ str(b))
	b = b >> offset%16 & 0b1
	return int(str(b))

def m2c(s, offset=0): # msg16 -> int64 ####################################
	s4 = s[offset:offset+1]
	return int(s4)

def m2i(m, sgn="-", offset=0): # msg16 -> int64
	m16 = m[offset*2+1] * 256 + m[offset*2]
	if sgn !="u" and sgn !="U":
		i = np.array(m16, dtype=np.int16)
	else:
		i = np.array(m16, dtype=np.uint16)
	return int(str(i))


def m2d(m, sgn="-", offset=0): # msg32 -> int64
	m32 = m[offset*2+3] * 16777216 + m[offset*2+2] * 65536 + m[offset*2+1] * 256 + m[offset*2+0]
	if sgn !="u" and sgn !="U":
		d = np.array(m32, dtype=np.int32)
	else:
		d = np.array(m32, dtype=np.uint32)
	return int(str(d))


def m2f(m, offset=0): # msg32 -> float64
	m32 = m[offset*2+3] * 16777216 + m[offset*2+2] * 65536 + m[offset*2+1] * 256 + m[offset*2]
	f = np.array(m32, dtype=np.uint32)
	return struct.unpack('<f', f)[0]
	
#	s32 = s[offset*4+4:offset*4+8] + s[offset*4:offset*4+4]
#	return struct.unpack('>f', binascii.unhexlify(s32))[0]



def i2m(d, sgn="-"): # int -> msg8
	if sgn != "u" and sgn != "U":
		d += 65536 * (d<0)
	q, mod = divmod(d, 256)
	return np.array([mod, q], dtype=msg8)

def d2m(d, sgn="-"): # int -> msg32
	if sgn != "u" and sgn != "U":
		d += 4294967296 * (d<0)
	q, mod = divmod(d, 65536)
	q1, mod1 = divmod(mod, 256)
	q2, mod2 = divmod(q, 256)
	return np.array([mod1, q1, mod2, q2], dtype=msg8)

def f2m(r): # float -> msg32
	f = struct.unpack('>I', struct.pack('>f', r))[0]
	q, mod = divmod(f, 65536)
	q1, mod1 = divmod(mod, 256)
	q2, mod2 = divmod(q, 256)
	return np.array([mod1, q1, mod2, q2], dtype=msg8)

#	s = hex(struct.unpack('>I', struct.pack('>f', r))[0]).upper()
#	return  s[6:10] + s[2:6]


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


def print_response(res):
	p = response_head
	print(res[:p-2])
	print(res[p-2:p])
	print(res[p:])
#	d = res[p:]
#	print(d.reshape(len(d)/2,2))


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
		print(str(f2m(n)) + " -> " + str((m2f(f2m(n)))))
		# print(f2m(n) + " (IEEE754 : " + f2m(n)[-4:] + f2m(n)[:4] + ") -> " + str((m2f(f2m(n)))))
	else:
		n = int(s)
		b = input("Number is 16bit or 32bit ? [16/32] : ")
		u = input("Number is unsigned or signed ? [u/s] : ")
		if   b == "16" and u == "s": #           -32,768 - 32,767
			print( str(i2m(n)) + " -> " + str(m2i(i2m(n))) )
		elif b == "16" and u == "u": #                 0 - 65,535
			print( str(i2m(n, u)) + " -> " + str(m2i(i2m(n, u))) )
		elif b == "32" and u == "s": #    -2,147,483,648 - 2,147,483,647
			print( str(d2m(n)) + " -> " + str(m2d(d2m(n))) )
		elif b == "32" and u == "u": #                 0 - 4,294,967,295
			print( str(d2m(n, u)) + " -> " + str(m2d(d2m(n, u))) )

