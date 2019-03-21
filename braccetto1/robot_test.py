import abb
R = abb.Robot(ip='192.168.125.1')
R.set_speed([150,150,150,150])
R.set_joints([0,0,0,0,0,0])


# R.set_speed([150,50,50,50])
# Middle Left
R.set_cartesian([[1000, 0, 800], [0,0,1,0]])

# Top Left
R.set_cartesian([[1000, 700, 900], [0,0,1,0]])

# Bottom Middle
R.set_cartesian([[1100, 650, 1050], [0,0,1,0]])

# Top Right
R.set_cartesian([[1200, 600, 1100], [0,0,1,0]])

# Middle Right
R.set_cartesian([[1200, 0, 1100], [0,0,1,0]])

# Bottom Right
R.set_cartesian([[1200, -600, 1100], [0,0,1,0]])

# Bottom Middle
R.set_cartesian([[1100, -650, 1050], [0,0,1,0]])

# Bottom Left
R.set_cartesian([[1000, -700, 900], [0,0,1,0]])

# Middle Left
R.set_cartesian([[1000, 0, 800], [0,0,1,0]])

R.close()