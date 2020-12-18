#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
 #  2020.12.18
 #  face_reco.py
 #  ver 1.0
 #  Kunihito Mitsuboshi
 #  license(Apache-2.0) at http://www.apache.org/licenses/LICENSE-2.0
 ##

from logging import getLogger, config
import face_recognition as fr
import numpy as np
import cv2
import sys
import os

config.fileConfig("python_log_config.ini")
logger = getLogger("develop")

known_face_encodings = []
known_face_names = []

args = sys.argv
if len(args) < 2:
	logger.error("No image file found.")
	exit(1)
try:
	for img in args[1:]:
		known_face_encodings.append(fr.face_encodings(fr.load_image_file(img))[0])
		known_face_names.append(os.path.basename(img).split(".")[-2])

except Exception as errmsg:
	logger.error("%s", errmsg)
	exit(1)

logger.info("%d faces input.", len(known_face_names))

c = cv2.VideoCapture(0)


while True:
	_, frame = c.read()

	frame4dlib = frame[:, :, ::-1]

	face_locations = fr.face_locations(frame4dlib)
	face_encodings = fr.face_encodings(frame4dlib, face_locations)

	for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
		matches = fr.compare_faces(known_face_encodings, face_encoding)

		name = "Unknown"

		face_distances = fr.face_distance(known_face_encodings, face_encoding)
		best_match_index = np.argmin(face_distances)
		if matches[best_match_index]:
			name = known_face_names[best_match_index]

		cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

		cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
		font = cv2.FONT_HERSHEY_DUPLEX
		cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

	cv2.imshow("webcamera ( ESC:quit )", frame)

	if cv2.waitKey(1) & 0xFF == 27:
		break

c.release()
cv2.destroyAllWindows()