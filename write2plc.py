#!/usr/bin/env python
# -*- coding: utf-8 -*-


##
 #  2024.7.21
 #  write2plc.py
 #  ver.1.6
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##


# e.g.  ./write2plc.py -a 192.168.1.163:5010
# e.g.  ./write2plc.py -b 192.168.1.163:5011
# e.g.  ./write2plc.py -h 192.168.1.163:8501



import struct
import sys
import socket


arg = sys.argv

plc_type = 0
IP = ""
for c in range(len(arg)):
	if arg[c][0] == "-":
		if   arg[c][1] == "a": # MC-ascii
			plc_type = 1
		elif arg[c][1] == "b": # MC-binary
			plc_type = 2
		elif arg[c][1] == "h": # hostlink
			plc_type = 3
	elif ":" in arg[c]:
		IP = arg[c][:arg[c].find(":")]
		PORT = int(arg[c][arg[c].find(":")+1:])

if plc_type == 0:
	print("Unknown PLC")
	exit(0)



word_data = [-32768,  -3894,   -3893,   -256,     -1,      0,    255,   3893,  32767]
#            0x8000, 0xF0CA,  0xF0CB, 0xFF00, 0xFFFF, 0x0000, 0x00FF, 0x0F35, 0x7FFF

bit_data = [0b0000111100110101, 0b1111000011001010, 0b1111111111111111]
#                       0x0F35,             0xF0CA,             0xFFFF



# data for mitsubishi MC-ascii
wdata4ma = ""
for i in range(len(word_data)):
	wdata4ma += struct.pack('>h', word_data[i]).hex().upper()

bdata4ma = ""
for i in range(len(bit_data)):
	bdata4ma += struct.pack('>H', bit_data[i]).hex().upper()



# data for mitsubishi MC-binary (little endian)
wdata4mb = b''
for i in range(len(word_data)):
	wdata4mb += struct.pack('<h', word_data[i])

bdata4mb = b''
for i in range(len(bit_data)):
	bdata4mb += struct.pack('<H', bit_data[i])



# data for keyence host link
wdata4hl = ""
for i in range(len(word_data)):
	wdata4hl += " " + ("+" if word_data[i]>0 else "") + str(word_data[i])

bdata4hl = ""
for i in range(len(bit_data)):
	for j in range(16):
		bdata4hl += " " + str(bit_data[i]%2)
		bit_data[i] //= 2



if   plc_type == 1:

	length = 4 + 12 + 8 + 4 + 4*len(word_data) + 8 + 4 + 4*len(bit_data)                 # 88
	head1 = "500000FF03FF00"
	head2 = format(length, "04X")                                                        # "0058"
	head3 = "0000"                                                      #  4 byte
	command = "140600000101"                                            # 12 byte
	w_dev = "W*000100" # W100                                           #  8 byte
	w_num = format(len(word_data), "04X")                               #  4 byte        # "0009"
#	wdata4ma                                                            # 36 byte
	b_dev = "B*000100" # B100                                           #  8 byte
	b_num = format(len(bit_data), "04X")                                #  4 byte        # "0003"
#	bdata4ma                                                            # 12 byte

	msg = (head1 + head2 + head3 + command + w_dev + w_num + wdata4ma + b_dev + b_num + bdata4ma).encode()
	req = [msg]
	success = ("D00000FF03FF0000040000").encode()

elif plc_type == 2:

	length = 2 + 6 + 4 + 2 + 2*len(word_data) + 4 + 2 + 2*len(bit_data)                  # 44
	head1 = b'\x50\x00\x00\xFF\xFF\x03\x00'
	head2 = struct.pack('<h', length)                                                    # b'\x2C\x00'
	head3 = b'\x00\x00'                                                 #  2 byte
	command = b'\x06\x14\x00\x00\x01\x01'                               #  6 byte
	w_dev = b'\x00\x01\x00\xB4' # W100                                  #  4 byte
	w_num = struct.pack('<h', len(word_data))                           #  2 byte        # b'\x09\x00'
#	wdata4mb                                                            # 18 byte
	b_dev = b'\x00\x01\x00\xA0' # B100                                  #  4 byte
	b_num = struct.pack('<h', len(bit_data))                            #  2 byte        # b'\x03\x00'
#	bdata4mb                                                            #  6 byte

	msg = head1 + head2 + head3 + command + w_dev + w_num + wdata4mb + b_dev + b_num + bdata4mb
	req = [msg]
	success = b'\xD0\x00\x00\xFF\xFF\x03\x00\x02\x00\x00\x00'

elif plc_type == 3:

	command = "WRS "
	w_dev = "DM8000.S " # DM8000 as signed dec
	b_dev = "MR8000 "   # MR8000 as bit
	w_num = str(len(word_data))                                                          # "9"
	b_num = str(len(bit_data) * 16)                                                      # "48"

	msg1 = (command + w_dev + w_num + wdata4hl + "\r").encode()
	msg2 = (command + b_dev + b_num + bdata4hl + "\r").encode()
	req = [msg1, msg2]
	success = ("OK\r\n").encode() # b'\x4F\x4B\x0D\x0A'


for n in range(len(req)):
	# print("REQUEST DATA : " + req[i].hex().upper())
	reqstr = req[n].hex().upper()
	for i in range(int(len(reqstr)/32)+1):
		print_line = "REQUEST DATA : " if i==0 else " "*15
		for j in range(16):
			k = i * 16 + j
			if len(reqstr) > k*2:
				print_line += reqstr[k*2:(k+1)*2] + ("  " if j == 7 else " ")
		print(print_line)


if len(IP) == 0: exit(0)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))

for n in range(len(req)):
	s.send(req[n])

	res = s.recv(4096)
	if plc_type == 1 or plc_type == 3:
		print("RESPONSE DATA : " + res.decode())
	else:
		print("RESPONSE DATA :", res)

	if res == success:
		print("Sended data success")

s.close()
