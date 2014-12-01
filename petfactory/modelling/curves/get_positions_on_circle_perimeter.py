import pymel.core as pm
import math

def loc(x,y,z=0):
    loc = pm.spaceLocator()
    loc.translate.set((x,y,z))
    loc.getShape().localScale.set(.05, .05, .05)
    
# the hypoytenuse
crv = pm.PyNode('crv')
pos_list = crv.getCVs()
r = 1.0
circ_center = pm.datatypes.Vector(2,1,0)


#The angle of the mid vector, i.e. the shared hypotenuse
theta = math.atan2(pos_list[1].y, pos_list[1].x)
#print(pm.util.degrees(theta))

# the angle we need to rpotate from positive x axis to the theta angle
ang = math.pi + theta
#ang_deg = pm.util.degrees(ang)

# the angle between theta and the oposite side of the right triangle (1.5 PI)
dif_ang = math.pi*1.5 - ang

num_points = 5
ang_inc = dif_ang / (num_points+1)

for i in range(num_points):
    
    #dif_ang_half = dif_ang * .5
    rot = ang + ang_inc * (i+1)
    rot_deg = pm.util.degrees(rot)
    #line = pm.curve(d=1, p=[(0,0,0), (2,0,0)])
    #line.translate.set(2,1,0)
    #line.rotate.set(0,0,rot_deg)
    
    x = (math.cos(rot)) + circ_center.x
    y = (math.sin(rot)) + circ_center.y
    
    loc(x,y)

