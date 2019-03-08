import cv2
from imutils.video import VideoStream
import numpy as np
import math
import imutils
import time
import abb

robot_ip = "192.168.125.1"
AXIS_RANGE_X = [650, 1200]
AXIS_RANGE_Y = [-750, 750] # Right = -650, Left = 650
AXIS_RANGE_Z = [1200, 300]
(LEFT,CENTER,RIGHT) = (0,1,2)
STARTING_POSITION = CENTER
GLOBAL_POS_X = int((AXIS_RANGE_X[0]+AXIS_RANGE_X[1])/2)
GLOBAL_POS_Y = int((AXIS_RANGE_Y[0]+AXIS_RANGE_Y[1])/2)
GLOBAL_POS_Z = int((AXIS_RANGE_Z[0]+AXIS_RANGE_Z[1])/2)
if STARTING_POSITION == LEFT:
	GLOBAL_POS_Y = int(AXIS_RANGE_Y[1])
	GLOBAL_POS_Z = AXIS_RANGE_Z[1]
elif STARTING_POSITION == RIGHT:
	GLOBAL_POS_Y = int(AXIS_RANGE_Y[0])
qOrientation = [0,0,1,0] # Quaternion Orientation

rho = 1
theta = np.pi/180
threshold = 20	 	# Minimum vote it should get for it to be considered as a line.
minLineLength = 10	# Minimum length of line. Line segments shorter than this are rejected.
maxLineGap = 10		# Maximum allowed gap between line segments to treat them as single line.
apertureSize = 3

def sortX(val): 
    return val[0]
def sortY(val): 
    return val[1]

def auto_canny(img, sigma=0.25):
	# compute the median of the single channel pixel intensities
	v = np.median(img)
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(img, lower, upper, apertureSize)
	return edged

def auto_thresh(img, sigma=0.25):
	# compute the median of the single channel pixel intensities
	v = np.median(img)
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (0.9 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	ret,th1 = cv2.threshold(img,lower, upper, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	ret,thresh = cv2.threshold(th1, lower, upper, cv2.THRESH_BINARY_INV)
	return thresh


a = 0
try:
    print ("Connecting to %s ..." % (robot_ip))
    R = abb.Robot(ip=robot_ip)
    print ("\t+ Successfully connected to %s." % (robot_ip))
    print ("\t+ %s." % (R.get_robotinfo()))
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
print("GLOBAL_POS_X = %s mm" % (ROBOT_POS_X))
print("GLOBAL_POS_Y = %s mm" % (ROBOT_POS_Y))
print("GLOBAL_POS_Z = %s mm" % (ROBOT_POS_Z))

R.set_speed([100,150,150,150])
R.set_cartesian([[GLOBAL_POS_X, GLOBAL_POS_Y, GLOBAL_POS_Z], qOrientation])
R.close()
exit()



vs = None
vs = VideoStream(src=0).start()
# vs = cv2.VideoCapture("linemovement.mp4")
time.sleep(2.0)

(W, H, center_x, center_y) = (None, None, 0, 0)
target_offset = 5

while True:
	# frame = cv2.imread("lines.png")
	# frame = cv2.imread("lines.jpg")
	# frame = cv2.imread("curved.jpg")
	# frame = cv2.imread("curveline.png")
	frame = vs.read()
	frame = imutils.resize(frame, width=800)
	# frame = imutils.resize(frame[1], width=800)
	test_frame = frame.copy()
	frame_copy = frame.copy()
	if W is None or H is None:
		(H, W) = frame.shape[:2]
		center_x = int(W/2)
		center_y = int(H/2)

	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray, (5,5), 0)

	'''
	# Draw contours of lines
	ret,th1 = cv2.threshold(blur,35,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	ret,thresh = cv2.threshold(th1, 100, 255, cv2.THRESH_BINARY_INV)
	# thresh = auto_thresh(blur)
	mask = cv2.erode(thresh, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	# im2,contours,hierarchy = cv2.findContours(thresh, 1, cv2.CHAIN_APPROX_NONE)
	im2,contours,hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	if len(contours) > 0:
		c = max(contours, key=cv2.contourArea)
		M = cv2.moments(c)
		(cx,cy) = (0,0)
		if M['m00'] != 0:
			cx = int(M['m10']/M['m00'])
			cy = int(M['m01']/M['m00'])
		cv2.line(frame_copy, (cx,0), (cx,H), (255,0,0), 2)
		cv2.line(frame_copy, (0,cy), (W,cy), (255,0,0), 2)
		cv2.drawContours(frame_copy, contours, -1, (0,255,0), 2)
	'''

	# Continue drawing edges of lines
	edges = auto_canny(blur)
	lines = cv2.HoughLinesP(edges, rho, theta, threshold, minLineLength, maxLineGap)
	if lines is not None:
		# max_line_length = 0
		# min_distance = 0
		# starting_coor = [0,0]
		# closest_coords = [0,0]
		# temp_coords = [0,0]
		
		target_distance = 9999
		for line in lines:
			x2,y2,x1,y1 = line[0]
			# Draw detected line segment
			cv2.line(frame, (x1,y1), (x2,y2), (0,0,255), 2)

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

		print("target_pos_x:%d target_pos_y:%d distance:%d" % (target_pos_x,target_pos_y,target_distance))
		cv2.line(frame, (target_pos_x,target_pos_y), (center_x,center_y), (100,100,20), 2)

		if target_pos_x > center_x:
			temp_pos_y = GLOBAL_POS_Y - 5
			GLOBAL_POS_Y = max(temp_pos_y, AXIS_RANGE_Y[0])
		else:
			temp_pos_y = GLOBAL_POS_Y + 5
			GLOBAL_POS_Y = max(temp_pos_y, AXIS_RANGE_Y[0])

		R.set_cartesian([[GLOBAL_POS_X, GLOBAL_POS_Y, GLOBAL_POS_Z], qOrientation])

		# if target_pos_y > target_offset:
		# 	temp_pos_x = GLOBAL_POS_X - 10
		# 	GLOBAL_POS_X = max(temp_pos_x, AXIS_RANGE_X[0])
		# elif target_pos_y < -target_offset:
		# 	temp_pos_x = GLOBAL_POS_X + 10
		# 	GLOBAL_POS_X = min(temp_pos_x, AXIS_RANGE_X[1])

		# if target_pos_x > target_offset:
		# 	temp_pos_y = GLOBAL_POS_Y - 10
		# 	GLOBAL_POS_Y = max(temp_pos_y, AXIS_RANGE_Y[0])
		# elif target_pos_x < -target_offset:
		# 	temp_pos_y = GLOBAL_POS_Y + 10
		# 	GLOBAL_POS_Y = min(temp_pos_y, AXIS_RANGE_Y[1])

		# if target_pos_x < center_x and GLOBAL_POS_Y >= AXIS_RANGE_Y[0]:
		# 		pass

		# if STARTING_POSITION == LEFT:
		# 	if GLOBAL_POS_Y >= AXIS_RANGE_Y[1] or GLOBAL_POS_Y <= AXIS_RANGE_Y[0]:
		# 		pass
		# 	if target_pos_x < center_x and GLOBAL_POS_Y >= AXIS_RANGE_Y[0]:
		# 		pass
		# 	elif GLOBAL_POS_Y < 0 and GLOBAL_POS_Y >= AXIS_RANGE_Y[0]:
		# 		pass
			# d2 = min(math.sqrt(math.pow((x2),2)+math.pow((y2),2)),
					# math.sqrt(math.pow((x1),2)+math.pow((y1),2)))
			# if d1 < d2:
			# 	d = d1
			# 	temp_coords = [x1,y1]
			# else:
			# 	d = d2
			# 	temp_coords = [x2,y2]

			# if d < min_distance:
			# 	min_distance = d
			# 	closest_coords = temp_coords

			# if next_coords[0] < closest_coords[0]:

			# if next_coords[1] < closest_coords[1]:

			# Calculate the distance of a line segment, find the longest
			# mx = int((x1 + x2) / 2)
			# my = int((y1 + y2) / 2)
			# cv2.line(frame, (mx,my), (mx,my), (255,0,0), 8)
			# d = math.sqrt( math.pow((x2-x1),2) + math.pow((y2-y1),2) )
			# if max_line_length < d:
			# 	max_line_length = d
			# 	midX = mx
			# 	midY = my
			# print("{x1:%s y1:%s x2:%s y2:%s d:%d}" % (x1, y1, x2, y2, d))

		# Draw line segment from center point to longest line segment per frame
		# cv2.line(frame, (midX,midY), (int(W/2),int(H/2)), (100,100,20), 2)

		# target_pos_x = x-(W/2)
		# target_pos_y = (H/2)-y

		# new_pos_x = AXIS_RANGE_X[0]robot_get_cartesian = R.get_cartesian()
		# ROBOT_POS_X = robot_get_cartesian[0][0]
		# ROBOT_POS_Y = robot_get_cartesian[0][1]
		# ROBOT_POS_Z = robot_get_cartesian[0][2]

		# if target_pos_y > 20:
		# 	temp_pos_x = GLOBAL_POS_X - 10
		# 	GLOBAL_POS_X = max(temp_pos_x, AXIS_RANGE_X[0])
		# elif target_pos_y < -20:
		# 	temp_pos_x = GLOBAL_POS_X + 10
		# 	GLOBAL_POS_X = min(temp_pos_x, AXIS_RANGE_X[1])

		# if target_pos_x > 20:
		# 	temp_pos_y = GLOBAL_POS_Y - 10
		# 	GLOBAL_POS_Y = max(temp_pos_y, AXIS_RANGE_Y[0])
		# elif target_pos_x < -20:
		# 	temp_pos_y = GLOBAL_POS_Y + 10
		# 	GLOBAL_POS_Y = min(temp_pos_y, AXIS_RANGE_Y[1])

		# GLOBAL_POS_Z = AXIS_RANGE_Z[0]

		# print("{ x:%d, y:%d, r:%d } {x:%d, y:%d, z:%d }" % (target_pos_x, target_pos_y, radius, GLOBAL_POS_X, GLOBAL_POS_Y, GLOBAL_POS_Z))
		# R.set_cartesian([[GLOBAL_POS_X, GLOBAL_POS_Y, GLOBAL_POS_Z], qOrientation])

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

	# cv2.waitKey(0)
	# cv2.destroyAllWindows()
	# break

try:
	vs.stop()
except:
	pass
try:
	vs.release()
except:
	pass

cv2.destroyAllWindows()
# R.set_joints([0,0,0,0,0,0])
R.close()