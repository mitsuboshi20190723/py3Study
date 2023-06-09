#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
 #  2023.6.9
 #  teef.py
 #  ver 1.0
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##


def divide_zero(a):
	a = a / 0
	return a


def try_divide_zero(a):
	try:
		a = a / 0
	except:
		print("In try_divide_zero : divide by zero")
	return a


def try_divide_char(a):
	try:
		a = a / "a"
	except:
		print("In try_divide_char : divide by char")
	return a


if __name__ == "__main__":

	a=0
	cnt = 0

	try:
		a = 81 / 9
		cnt += 1

#		a = divide_zero(2)
		cnt += 1

		a = try_divide_zero(3)
		cnt += 1

#		a = 10 / "F"
		cnt += 1

		a = try_divide_char(5)
		cnt += 1

	except:
		print("In main : divide error")

	else:
		print(type(a), a)

	finally:
		print("counter =", cnt)


	print("end of main")
