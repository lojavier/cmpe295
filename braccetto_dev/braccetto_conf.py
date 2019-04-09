#!python
from enum import Enum

ROBOT_IP = "192.168.125.1"
AXIS_RANGE_X = [1000, 1200] # LEFT = 1000 <-> RIGHT = 1200
AXIS_RANGE_Y = [-600, 600] # DOWN = -600 <-> UP = 600
AXIS_RANGE_Z = [800, 1200] # lower = 900 <-> raise = 1300
Q_ORIENTATION = [0,0,1,0] # Quaternion Orientation
AXIS_THRESHOLD_Y = 300

AXIS_X_Z_RATIO = (AXIS_RANGE_X[1] - AXIS_RANGE_X[0]) / (AXIS_RANGE_Z[1] - AXIS_RANGE_Z[0]) # 0.5
AXIS_Y_Z_RATIO = AXIS_THRESHOLD_Y / (AXIS_RANGE_Z[1] - AXIS_RANGE_Z[0]) # 0.75

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

CROP_RATIO = [0.60, 0.20, 0.20, 0.60]	# [ L/R (W,H) <-> U/D(W,H) ]

ABB_MM_PX_RATIO_Y = 0.10
ABB_MM_PX_RATIO_Z = 0.20
ABB_MM_PX_RATIO_X = ABB_MM_PX_RATIO_Z * AXIS_X_Z_RATIO