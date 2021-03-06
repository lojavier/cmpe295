#!python
# Usage: python line_tracking.py -r y -v y -d n
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

T = 120

def select_black(image):
    # converted = convert_hls(image)
    converted = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
    # white color mask
    lower = np.uint8([  0,  0,   0])
    upper = np.uint8([5, 5, 5])
    black_mask = cv2.inRange(converted, lower, upper)
    mask = black_mask
    return cv2.bitwise_and(image, image, mask = mask)

def auto_canny(img, sigma=0.1):
	global apertureSize
	# compute the median of the single channel pixel intensities
	v = np.median(img)
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(img, lower, upper, apertureSize)
	return edged

def crop_roi(img, vertices):
	mask = np.zeros_like(img)
	match_mask_color = 255

	cv2.fillPoly(mask, vertices, match_mask_color)
	masked_image = cv2.bitwise_and(img, mask)
	return masked_image

def balance_frame(image, width, height):
	vertices = [(0, height), (width / 4, 3 * height / 4),(3 * width / 4, 3 * height / 4), (width, height),]
	vertices = np.array([vertices], np.int32)

	blank = np.zeros((height, width, 3), np.uint8)
	blank[:] = (255, 255, 255)
	blank_gray = cv2.cvtColor(blank, cv2.COLOR_BGR2GRAY)
	blank_cropped = crop_roi(blank_gray, vertices)
	area = cv2.countNonZero(blank_cropped)

	global T
	ret = None
	direction = 0
	for i in range(0, 10):
		rc, gray = cv2.threshold(image, T, 255, 0)
		crop = crop_roi(gray, vertices)
		nwh = cv2.countNonZero(crop)
		perc = int(100 * nwh / area)
		# logging.debug(("balance attempt", i, T, perc))
		if perc > 12:
			if T > 180:
				break
			if direction == -1:
				ret = crop
				break
			T += 10
			direction = 1
		elif perc < 3:
			if T < 40:
				break
			if  direction == 1:
				ret = crop
				break
			T -= 10
			direction = -1
		else:
			ret = crop
			break  
	return ret

def find_main_countour(image):
    im2, cnts, hierarchy = cv2.findContours(image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    C = None
    if cnts is not None and len(cnts) > 0:
         C = max(cnts, key = cv2.contourArea)
    if C is None:
        return None, None
    rect = cv2.minAreaRect(C)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    box = geom.order_box(box)
    return C, box
'''
def auto_thresh(img, sigma=0.25):
	# compute the median of the single channel pixel intensities
	v = np.median(img)
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (0.9 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	ret,th1 = cv2.threshold(img,lower, upper, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	ret,thresh = cv2.threshold(th1, lower, upper, cv2.THRESH_BINARY_INV)
	return thresh
'''

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
		frame = cv2.imread("lines.png")
		# frame = cv2.imread("lines.jpg")
		# frame = cv2.imread("curved.jpg")
		# frame = cv2.imread("curveline.png")
	frame = imutils.resize(frame, width=FRAME_WIDTH)
	frame_copy = frame.copy()

	if W is None or H is None:
		(H, W) = frame.shape[:2]
		(center_x, center_y) = (int(W/2), int(H/2))

	# black = select_black(frame)
	# gray = cv2.cvtColor(black, cv2.COLOR_BGR2GRAY)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray, (9,9), 0)
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
	crop = balance_frame(blur, W, H)
	cont, box = find_main_countour(crop)
	# p1, p2 = geom.calc_box_vector(box)
	# angle = geom.get_vert_angle(p1, p2, W, H)
	# shift = geom.get_horz_shift(p1[0], W)

	cv2.drawContours(frame, [cont], -1, (0,0,255), 3)
	cv2.drawContours(frame,[box],0,(255,0,0),2)
	# cv2.line(frame, p1, p2, (0, 255, 0), 3)
	# msg_a = "Angle {0}".format(int(angle))
	# msg_s = "Shift {0}".format(int(shift))

	# cv2.putText(frame, msg_a, (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
	# cv2.putText(frame, msg_s, (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

	cv2.imshow("crop", crop)
	cv2.imshow("Image", frame)
	
	if DEBUG_MODE:
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		break


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

	# update the FPS counter
	fps.update()

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
