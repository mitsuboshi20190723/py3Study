#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
 #  2020.11.22
 #  json4azure.py
 #  ver 1.0
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##

from logging import getLogger, config
import os
import sys

config.fileConfig("python_log_config.ini")
logger = getLogger("develop")


head =\
'\
	{\
		"key1" : "value1",\
		"data" : \
'

tail = ', "key2" : "value2" }'
# tail = '}'


args = sys.argv

if len(args) < 2:
	logger.error("Not JSON file or new dir name.")
	exit(1)
if os.path.exists(args[1]):
	logger.error("%s exist! : $ rm -rf %s", args[1], args[1])
	exit(1)
if len(args) < 3:
	logger.error("Not JSON file.")
	exit(1)

if args[1][-1] == "/":
	dir_name = args[1]
else:
	dir_name = args[1] + "/"
os.mkdir(dir_name)
count = 0

for file_name in args[2:]:
	azure_file_name = file_name.split("/")[-1]
	azure_file_name = azure_file_name[:-5] + "_azure.json"

	print(file_name + "   ->   " + dir_name + azure_file_name)

	try:
		jf = open(file_name, "r")
		data = jf.read()
		jf.close()

		ajf = open(dir_name + azure_file_name, "w")
		ajf.write(head + data + tail)
		ajf.close()

	except OSError as errmsg:
		logger.error("%s", errmsg)
		exit(1)

	count += 1

print("%d files changed.", count)
print("Prease type command  : $ zip -v " + dir_name[:-1] + ".zip " + dir_name + "*_azure.json")