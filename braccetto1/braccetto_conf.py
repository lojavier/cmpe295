#!python
from enum import Enum

ROBOT_IP = "192.168.125.1"
AXIS_RANGE_X = [650, 1200] # LEFT = 650 <-> RIGHT = 1200
AXIS_RANGE_Y = [-750, 750] # DOWN = -750 <-> UP = 750
AXIS_RANGE_Z = [300, 1200] # BOTTOM = 300 <-> TOP = 1200
Q_ORIENTATION = [0,0,1,0] # Quaternion Orientation

MAX_FRAME_WIDTH = 800

class DIRECTION(Enum):
	LEFT = 0
	RIGHT = 1
	UP = 2
	DOWN = 3

# rho = 1
# theta = np.pi/180
THRESHOLD = 120	 	# Minimum vote it should get for it to be considered as a line.
# minLineLength = 10	# Minimum length of line. Line segments shorter than this are rejected.
# maxLineGap = 10		# Maximum allowed gap between line segments to treat them as single line.
# apertureSize = 3

CROP_RATIO = [0.75, 0.40, 0.40, 0.90]	# [ L/R(x,y), F/B(x,y) ]
ABB_MM_PX_RATIO = 5
