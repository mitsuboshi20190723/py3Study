#!/usr/bin/env python
# -*- coding: utf-8 -*-


##
 #  2024.6.3
 #  write2plc.py
 #  ver.1.2
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##


# e.g. ./write2plc -a 192.168.1.163:5010
# e.g. ./write2plc -b 192.168.1.163:5011
# e.g. ./write2plc -h 192.168.1.163:8501



import struct
import sys
import socket


arg = sys.argv

plc_type = 0 # if cording "plc_type = 4" then PLC type is MC-ascii
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



word_data = [15, 100, 1024, 32767, 180, 0, -180, -32768]

bit_data = [0b0101010101010101, 0b1010101010101010]
#                       0x5555,             0xAAAA
#                        21845,              43690


# data for mitsubishi MC protocol
wdata4mc = b''
for i in range(len(word_data)):
	wdata4mc += struct.pack('h', word_data[i])

bdata4mc = b''
for i in range(len(bit_data)):
	bdata4mc += struct.pack('H', bit_data[i])

# data for keyence host link
wdata4hl = ""
for i in range(len(word_data)):
	wdata4hl += " " + str(word_data[i])

bdata4hl = ""
for i in range(len(bit_data)):
	bdata4hl += " " + str(bit_data[i])
#	bdata4hl += " " + str(hex(bit_data[i]).hex().upper())



if   plc_type == 1:

	length = 4 + 12 + 8 + 4 + 2*len(word_data) + 8 + 4 + 2*len(bit_data)
	head1 = "500000FF03FF00"
	head2 = format(length, "04X")
	head3 = "0000"                                                      #  4 byte
	command = "140600000101"                                            # 12 byte
	w_dev = "W*000100" # W100                                           #  8 byte
	w_num = format(len(word_data), "04X")                               #  4 byte

	b_dev = "B*000100" # B100                                           #  8 byte
	b_num = format(len(bit_data), "04X")                                #  4 byte

	msg = (head1 + head2 + head3 + command + w_dev + w_num).encode() + wdata4mc + (b_dev + b_num).encode() + bdata4mc
	req = [msg]
	success = ("D00000FF03FF0000040000").encode()

elif plc_type == 4:

	length = 4 + 12 + 8 + 4 + 2*len(word_data) + 8 + 4 + 2*len(bit_data)
	head1 = b'\x35\x30\x30\x30\x30\x30\x46\x46\x30\x33\x46\x46\x30\x30'
	head2 = format(length, "04X").encode()
	head3 = b'\x30\x30\x30\x30'                                         #  4 byte
	command = b'\x31\x34\x30\x36\x30\x30\x30\x30\x30\x41\x30\x31'       # 12 byte
	w_dev = b'\x57\x2A\x30\x30\x30\x41\x30\x30' # W100                  #  8 byte
	w_num = format(len(word_data), "04X").encode()                      #  4 byte

	b_dev = b'\x57\x2A\x30\x30\x30\x41\x30\x30' # B100                  #  8 byte
	b_num = format(len(bit_data), "04X").encode()                       #  4 byte

	msg = head1 + head2 + head3 + command + w_dev + w_num + wdata4mc + b_dev + b_num + bdata4mc
	req = [msg]
	success = b'\x44\x30\x30\x30\x30\x30\x46\x46\x30\x33\x46\x46\x30\x30\x30\x30\x30\x34\x30\x30\x30\x30'

elif plc_type == 2:

	length = 2 + 6 + 4 + 2 + 2*len(word_data) + 4 + 2 + 2*len(bit_data)
	head1 = b'\x50\x00\x00\xFF\xFF\x03\x00'
	head2 = struct.pack('h', length)
	head3 = b'\x00\x00'                                                 #  2 byte
	command = b'\x06\x14\x00\x00\x01\x01'                               #  6 byte
	w_dev = b'\x00\x01\x00\xB4' # W100                                  #  4 byte
	w_num = struct.pack('h', len(word_data))                            #  2 byte  

	b_dev = b'\x00\x01\x00\xA0' # B100                                  #  4 byte
	b_num = struct.pack('h', len(bit_data))                             #  2 byte

	msg = head1 + head2 + head3 + command + w_dev + w_num + wdata4mc + b_dev + b_num + bdata4mc
	req = [msg]
	success = b'\xD0\x00\x00\xFF\xFF\x03\x00\x06\x00'

elif plc_type == 3:

	command = "WRS "
	w_dev = "DW 9000.S " # DW9000 as signed dec
	b_dev = "MR 9000.H " # MR9000 as unsigned hex
	w_num = str(len(word_data))
	b_num = str(len(bit_data)) 

	msg1 = (command + w_dev + w_num + wdata4hl).encode() + b'\x0D'
	msg2 = (command + b_dev + b_num + bdata4hl).encode() + b'\x0D'
	req = [msg1, msg2]
	success = ("").encode()


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

# exit(0)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))

for n in range(len(req)):
	s.send(req[n])

	res = s.recv(4096)
	if plc_type == 1 or plc_type == 3:
		res = res.decode()
	print("RESPONSE DATA : " + res)

	if res == success:
		print("Sended Data success")

s.close()
