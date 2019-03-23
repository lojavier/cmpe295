#!python
from enum import Enum

ROBOT_IP = "192.168.125.1"
AXIS_RANGE_X = [1000, 1200] # LEFT = 1000 <-> RIGHT = 1200
AXIS_RANGE_Y = [-650, 650] # DOWN = -750 <-> UP = 750
AXIS_RANGE_Z = [850, 1050] # lower = 1000 <-> raise = 1200
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

CROP_RATIO = [0.80, 0.40, 0.40, 0.80]	# [ L/R(x,y), U/D(x,y) ]
ABB_MM_PX_RATIO_X = 12
ABB_MM_PX_RATIO_Y = 10
ABB_MM_PX_RATIO_Z = 12