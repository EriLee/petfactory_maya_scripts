import pymel.core as pm
import math

def rot(ang_rad):
    obj = pm.curve(degree=1, p=[(0,0,0), (10,0,0)])
    obj.rotate.set(pm.util.degrees((0, 0, ang_rad)))

def line(s, e):
    pm.curve(degree=1, p=[s, e])

def loc(pos):
    loc = pm.spaceLocator()
    loc.translate.set(pos)
    loc.getShape().localScale.set(.2,.2,.2)

# radius of circle
radius = 1

# the length of the visual debug mid vector
vec_length = 10

# get the curve
crv = pm.PyNode('crv')
# get the cv positions
pos_list = crv.getShape().getCVs(space='world')

# get the vector B - A (second to first cv)
ba_vec = (pos_list[0] - pos_list[1])
# get the vector B - C (second to third cv)
bc_vec = (pos_list[2] - pos_list[1])

# normalize the vectors
ba_vec_n = ba_vec.normal()
bc_vec_n = bc_vec.normal()

# calculate the mid vector
mid_vec_n = (ba_vec_n + bc_vec_n).normal()

# get the angle of the vectors
theta_ba = math.atan2(ba_vec_n.y, ba_vec_n.x)
theta_bc = math.atan2(bc_vec_n.y, bc_vec_n.x)

# If the angle of BA is less than angle BC
# we subbtract angle BA from angle BC
# we also divide the angle with 2 to get the
# angle in the "triangle"
if theta_ba < theta_bc:
    theta_rad = (theta_bc - theta_ba)/2
else:
    theta_rad = (theta_ba - theta_bc)/2
    
# find where on the hypotenuse the circle should be drawn
# i.e. get the length of the hypotenuse in the right triangle
# using angle theta and the radius (opposite leg)
h = radius / math.sin(theta_rad)
#print(h)



# draw the mid line
line(pos_list[1], pos_list[1]+mid_vec_n*vec_length)


# get the circle cenyter position
circ_center = mid_vec_n*h
circ = pm.circle(r=radius, normal=(0,0,1))[0]
circ.translate.set(pos_list[1]+circ_center)



