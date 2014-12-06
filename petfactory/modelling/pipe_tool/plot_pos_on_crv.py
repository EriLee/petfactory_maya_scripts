import pymel.core as pm
import maya.cmds as cmds
import pprint
import math

#pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)
pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/empty_scene.mb', f=True)


def pos(p, size=.2):
    loc = pm.spaceLocator()
    loc.localScale.set((size,size,size))
    loc.translate.set(p)

radius = 3
theta = math.pi/6
num_points = 6

# The total angle in a triangle is 180 degrees
# since one angle is 90 deg (pi/2) and the theta ang is known, we can
# get the remaining angle with 180 - 90 - theta, which can be simplified to
# 90 - theta i.e. (math.pi/2) - theta
ang_opp = (math.pi/2) - theta

# get the adjacent given the opposite (radius) and the angle theta
# math.tan(theta) = o/a
# a * math.tan(theta) = o
# a = a / math.tan(theta)
adjacent = radius / math.tan(theta)

# create the vector to reflect about
mid_vec = pm.datatypes.Vector(adjacent, radius, 0)

# calculate the positions on the circle
ang_inc = ang_opp/(num_points-1)

pos_on_circ= []
for i in range(num_points):
    
    a = (1.5 * math.pi) - (ang_inc * i)
    x = math.cos(a) * radius + adjacent
    y = math.sin(a) * radius + radius
    pos_on_circ.append(pm.datatypes.Vector(x, y, 0))
    

# reflect the pos on circle across the mid vec  
pos_on_circ_reflected = [ 2 * pos_on_circ[i].dot(mid_vec) / mid_vec.dot(mid_vec) * mid_vec - pos_on_circ[i] for i in range(num_points-1) ]

# combine the pos and the reflected pos
pos_on_circ_reflected.reverse()
radius_pos_list =  pos_on_circ + pos_on_circ_reflected

# visualize
for p in radius_pos_list:
    pos(p)

 
crv_theta = pm.curve(d=1, p=[(0,0,0),(8,0,0)])
crv_ang_diff = pm.curve(d=1, p=[(0,0,0),(8,0,0)])
   
crv_theta.rotate.set((0, 0, pm.util.degrees(theta)))
#crv_ang_diff.rotate.set((0, 0, pm.util.degrees(ang_opp)))

circ = pm.circle(radius=radius)[0]
circ.translate.set(adjacent, radius, 0)

pos((adjacent, radius, 0), size=4)



