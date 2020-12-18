#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
 #  2020.12.18
 #  face_regi.py
 #  ver 1.5
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##

from logging import getLogger, config
import tkinter
import cv2

config.fileConfig("python_log_config.ini")
logger = getLogger("develop")


c = cv2.VideoCapture(0)

if not c.isOpened():
	logger.error("Do not open camera.")
	exit(1)

while True:
	_, frame = c.read()

	cv2.imshow("Webcamera ( ESC:quit, s:shutter )", frame)

	key = cv2.waitKey(1) & 0xFF
	if   key == ord('s'):
		tki = tkinter.Tk()
		tki.geometry('300x100')
		tki.title("What your name ?")
		t = tkinter.Entry(width=20)
		t.place(x=90, y=30)
		l = tkinter.Label(text="Name :")
		l.place(x=38, y=30)
		def getname():
			name = t.get()
			if len(name) > 0 and len(name) < 21:
				cv2.imwrite("./" + name + ".jpg", frame)
		b = tkinter.Button(tki, text="Create image file", command=getname)
		b.place(x=90, y=70)
		tki.mainloop()

	elif key == 27: # ESC
		break

cv2.destroyWindow("frame")

c.release()