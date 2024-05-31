#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
 #  2024.5.31
 #  days_of_year.py
 #  ver.1.0
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##


import sys
import json


with open("months.json", "r") as jf: days_of_month = json.load(jf)


args = sys.argv

leap = 0
if len(args) > 1:
	if args[1][1] == "l":
		leap = 1
	else:
		exit(0)

d = 0
d += int(days_of_month["January"])
d += int(days_of_month["February"][leap])
d += int(days_of_month["March"])
d += int(days_of_month["April"])
d += int(days_of_month["May"])
d += int(days_of_month["June"])
d += int(days_of_month["July"])
d += int(days_of_month["August"])
d += int(days_of_month["September"])
d += int(days_of_month["October"])
d += int(days_of_month["November"])
d += int(days_of_month["December"])

print(d, "days")
