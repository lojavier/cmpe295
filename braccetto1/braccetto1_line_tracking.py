#!python
# Usage: python line_tracking.py -r y -v y -d n
# http://einsteiniumstudios.com/beaglebone-opencv-line-following-robot.html
# https://medium.com/@const.toporov/line-following-robot-with-opencv-and-contour-based-approach-417b90f2c298
# https://medium.com/@mrhwick/simple-lane-detection-with-opencv-bfeb6ae54ec0
import cv2
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import math
import imutils
import time
import abb
import geom_util as geom
import roi
import track_cv as track
import track_conf as tconf

ap = argparse.ArgumentParser()
ap.add_argument("-r", "--robot", help="enable robot mode")
ap.add_argument("-v", "--video", help="enable video mode")
ap.add_argument("-d", "--debug", help="enable debug mode")
args = vars(ap.parse_args())

ROBOT_MODE = True if args["robot"] == "y" else False
VIDEO_MODE = True if args["video"] == "y" else False
DEBUG_MODE = True if args["debug"] == "y" else False

robot_ip = "192.168.125.1"
AXIS_RANGE_X = [650, 1200] # Compact = 650, Extended = 1200
AXIS_RANGE_Y = [-750, 750] # Right = -750, Left = 750
AXIS_RANGE_Z = [1200, 300] # Top = 1200, Bottom = 300
qOrientation = [0,0,1,0] # Quaternion Orientation

GLOBAL_POS_X = int((AXIS_RANGE_X[0]+AXIS_RANGE_X[1])/2)
GLOBAL_POS_Y = int((AXIS_RANGE_Y[0]+AXIS_RANGE_Y[1])/2)
GLOBAL_POS_Z = int((AXIS_RANGE_Z[0]+AXIS_RANGE_Z[1])/2)

(LEFT,CENTER,RIGHT) = (0,1,2)
STARTING_POSITION = LEFT
if STARTING_POSITION == LEFT:
	GLOBAL_POS_Y = int(AXIS_RANGE_Y[1])
	GLOBAL_POS_Z = AXIS_RANGE_Z[1]
elif STARTING_POSITION == RIGHT:
	GLOBAL_POS_Y = int(AXIS_RANGE_Y[0])

rho = 1
theta = np.pi/180
threshold = 20	 	# Minimum vote it should get for it to be considered as a line.
minLineLength = 10	# Minimum length of line. Line segments shorter than this are rejected.
maxLineGap = 10		# Maximum allowed gap between line segments to treat them as single line.
apertureSize = 3
FRAME_WIDTH = 800

def auto_canny(img, sigma=0.1):
	global apertureSize
	# compute the median of the single channel pixel intensities
	v = np.median(img)
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(img, lower, upper, apertureSize)
	return edged

if ROBOT_MODE:
	a = 0
	try:
	    print ("Connecting to %s ..." % (robot_ip))
	    R = abb.Robot(ip=robot_ip)
	    print ("\t+ Successfully connected to %s" % (robot_ip))
	    print ("\t+ %s" % (R.get_robotinfo()))
	    # R.set_joints([0,0,0,0,0,0])
	except:
	    a = 1;
	    print ("\t- Error: Failed to connect to %s. Trying 127.0.0.1 now ..." % (robot_ip))
	if(a == 1):
		try:
		    print ("Connecting to 127.0.0.1 ...")
		    R = abb.Robot(ip='127.0.0.1')
		except:
			print ("\t- Error: Failed to connect to 127.0.0.1. Exiting now.")
			exit(-1)

	robot_get_cartesian = R.get_cartesian()
	ROBOT_POS_X = robot_get_cartesian[0][0]
	ROBOT_POS_Y = robot_get_cartesian[0][1]
	ROBOT_POS_Z = robot_get_cartesian[0][2]
	print("robot_get_cartesian = %s" % (robot_get_cartesian))
	print("ROBOT_POS_X = %s mm" % (ROBOT_POS_X))
	print("ROBOT_POS_Y = %s mm" % (ROBOT_POS_Y))
	print("ROBOT_POS_Z = %s mm" % (ROBOT_POS_Z))
	R.set_speed([100,50,50,50])
	R.set_cartesian([[GLOBAL_POS_X, GLOBAL_POS_Y, GLOBAL_POS_Z], qOrientation])
	# R.close()
	# exit()

vs = None
frame = None
fps = None
(H, W) = (None, None)
(center_x, center_y) = (None, None)

if VIDEO_MODE or ROBOT_MODE:
	vs = VideoStream(src=0).start()
	time.sleep(2.0)

fps = FPS().start()

while True:
	if VIDEO_MODE or ROBOT_MODE:
		frame = vs.read()
	else:
		# frame = cv2.imread("lines.png")
		frame = cv2.imread("blackline1.jpg")
		# frame = cv2.imread("lab_line_example.jpg")
		# frame = cv2.imread("lab_line_example_Hflip.jpg")
		# frame = cv2.imread("curved.jpg")
		# frame = cv2.imread("curveline.png")
	frame = imutils.resize(frame, width=FRAME_WIDTH)
	(frame, angle, shift, W, H) = track.handle_frame(frame, None, True)
	
	if W is not None and H is not None:
		(center_x, center_y) = (int(W/2), int(H/2))
	
	if DEBUG_MODE:
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		break

		'''
	# Continue drawing edges of lines
	edges = auto_canny(blur)
	lines = cv2.HoughLinesP(edges, rho, theta, threshold, minLineLength, maxLineGap)
	if lines is not None:
		(target_pos_x, target_pos_y) = (0, 0)
		target_distance = FRAME_WIDTH
		for line in lines:
			x2,y2,x1,y1 = line[0]

			# Draw every line segment detected on the frame
			cv2.line(frame, (x1,y1), (x2,y2), (0,0,255), 2)

			# Adjust the coordinates, offsetting from the center of the frame
			temp_pos_x1 = x1 - center_x
			temp_pos_y1 = center_y - y1
			temp_pos_x2 = x2 - center_x
			temp_pos_y2 = center_y - y2
			temp_distance1 = math.sqrt(math.pow((temp_pos_x1),2)+math.pow((temp_pos_y1),2))
			temp_distance2 = math.sqrt(math.pow((temp_pos_x2),2)+math.pow((temp_pos_y2),2))
			
			if temp_distance1 < temp_distance2:
				temp_distance = temp_distance1
				temp_pos_x = x1
				temp_pos_y = y1
			else:
				temp_distance = temp_distance2
				temp_pos_x = x2
				temp_pos_y = y2

			if temp_distance < target_distance:
				target_distance = temp_distance
				target_pos_x = temp_pos_x
				target_pos_y = temp_pos_y

			# print("{x1:%d y1:%d} -> {x2:%d y2:%d} distance:%d" % (x1, y1, x2, y2, target_distance))

		# A line segment showing where the next target coordinates are located,
		# with relevance to the center point of the frame
		cv2.line(frame, (target_pos_x,target_pos_y), (center_x,center_y), (100,100,20), 2)

		# Logic to control the direction of the robot's movements
		if STARTING_POSITION == LEFT:
			if target_pos_x > center_x:
				temp_pos_y = GLOBAL_POS_Y - 5
				GLOBAL_POS_Y = max(temp_pos_y, AXIS_RANGE_Y[0])

		elif STARTING_POSITION == RIGHT:
			if target_pos_x < center_x:
				temp_pos_y = GLOBAL_POS_Y + 5
				GLOBAL_POS_Y = min(temp_pos_y, AXIS_RANGE_Y[1])

		if target_pos_y < center_y:
			temp_pos_x = GLOBAL_POS_X + 2
			GLOBAL_POS_X = max(temp_pos_x, AXIS_RANGE_X[0])
		elif target_pos_y > center_y:
			temp_pos_x = GLOBAL_POS_X - 2
			GLOBAL_POS_X = min(temp_pos_x, AXIS_RANGE_X[1])

		# print("{ x:%d, y:%d, r:%d } {x:%d, y:%d, z:%d }" % (target_pos_x, target_pos_y, radius, GLOBAL_POS_X, GLOBAL_POS_Y, GLOBAL_POS_Z))
		if ROBOT_MODE:
			R.set_cartesian([[GLOBAL_POS_X, GLOBAL_POS_Y, GLOBAL_POS_Z], qOrientation])

	# Add cross section line segments showing the center position within the frame
	cv2.line(frame, (center_x,0), (center_x,H), (253,106,2), 1)
	cv2.line(frame, (0,center_y), (W,center_y), (253,106,2), 1)

	# cv2.imshow("blurred", blurred)
	# cv2.imshow("edges", edges)
	# cv2.imshow("frame_copy", frame_copy)
	cv2.imshow("frame", frame)
	
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break
	if key == ord("s"):
		cv2.imwrite('lab_line_example.jpg', frame)

	if DEBUG_MODE:
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		break
	'''

	# update the FPS counter
	fps.update()

	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break

fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

try:
	vs.stop()
except:
	pass
try:
	vs.release()
except:
	pass

cv2.destroyAllWindows()

if ROBOT_MODE:
	# R.set_joints([0,0,0,0,0,0])
	R.close()
