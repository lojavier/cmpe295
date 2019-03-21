#!python
from enum import Enum

ROBOT_IP = "192.168.125.1"
AXIS_RANGE_X = [1000, 1200] # LEFT = 1000 <-> RIGHT = 1200
AXIS_RANGE_Y = [-600, 600] # DOWN = -750 <-> UP = 750
AXIS_RANGE_Z = [1000, 1200] # lower = 1000 <-> raise = 1200
Q_ORIENTATION = [0,0,1,0] # Quaternion Orientation
# Up right position
# if X < 850:
# 	Z >= 1000

# as X increases, Z should decrease, scale = 100
# 1250-850=400
# 1000-600=400
# Initialize
# R.set_cartesian([[850, 0, 1000], [0,0,1,0]])

# moved vertically upwards
# >>> R.set_cartesian([[1200, 0, 800], [0,0,1,0]])
# >>> R.set_cartesian([[1000, 0, 1000], [0,0,1,0]])

# as Y decreases, so does Z

# Bottom left corner
# R.set_cartesian([[1000, -700, 1000], [0,0,1,0]])
# Top left corner
# R.set_cartesian([[1000, 700, 1000], [0,0,1,0]])
# Top right corner
# R.set_cartesian([[1200, 600, 1100], [0,0,1,0]])
# Bottom right corner
# R.set_cartesian([[1200, -600, 1100], [0,0,1,0]])
# Middle right
# R.set_cartesian([[1200, 0, 1200], [0,0,1,0]])
# Middle left
# R.set_cartesian([[1100, 0, 800], [0,0,1,0]])


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
