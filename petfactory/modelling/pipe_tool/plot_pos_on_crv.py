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

def build_radius_t_matrix(radius, theta, num_points):
    
    # The total angle in a triangle is 180 degrees
    # since one angle is 90 deg (pi/2) and the theta ang is known, we can
    # get the remaining angle with 180 - 90 - theta, which can be simplified to
    # 90 - theta i.e. (math.pi/2) - theta, then we multiply by 2 to get the full circle
    # so we do not need to relect the vectors across the mid vec to get the full radius circ
    ang_full = ((math.pi/2) - theta) * 2
    
    # get the adjacent given the opposite (radius) and the angle theta
    # math.tan(theta) = o/a
    # a * math.tan(theta) = o
    # a = a / math.tan(theta)
    adjacent = radius / math.tan(theta)
    
    # create the vector to reflect about
    #mid_vec = pm.datatypes.Vector(adjacent, radius, 0)
    
    radius_center = pm.datatypes.Vector(adjacent, radius, 0)
    
    # calculate the positions on the circle
    ang_inc = ang_full/(num_points-1)
    
    # the ang from pos x axis to opposite (negative y axis)
    ang_to_opp = (1.5 * math.pi)
    
    t_matrix_list = []
    for i in range(num_points):
        
        a = ang_to_opp - (ang_inc * i)
        x = math.cos(a) * radius + adjacent
        y = math.sin(a) * radius + radius
        p = pm.datatypes.Vector(x, y, 0)
        
        # create the etransformation matrix
        aim = (radius_center - p).normal()
        up = pm.datatypes.Vector(0,0,1)
        cross = aim.cross(up)
        
        tm = pm.datatypes.TransformationMatrix( [ [aim.x, aim.y, aim.z, 0],
                                                  [cross.x, cross.y, cross.z, 0],
                                                  [up.x, up.y, up.z, 0],
                                                  [p.x, p.y, p.z, 1] ])
        t_matrix_list.append(tm)
        
    
    # visualize    
    #crv_theta = pm.curve(d=1, p=[(0,0,0),(8,0,0)])       
    #crv_theta.rotate.set((0, 0, pm.util.degrees(theta)))

    #circ = pm.circle(radius=radius)[0]
    #circ.translate.set(radius_center)
    
    # center locator    
    #pos((adjacent, radius, 0), size=4)
    
    
    return t_matrix_list


radius_t_matrix_list = build_radius_t_matrix(radius=3, theta=math.pi/6, num_points=12)

# get the matrix of the current sel to transform the matrix
cube = pm.polyCube()[0]
cube.translate.set(5,5,5)
cube.rotate.set(50,70,90)

tm = cube.getMatrix()

for i, p in enumerate(radius_t_matrix_list):
        sp = pm.polySphere(r=.2)[0]
        sp.setMatrix(radius_t_matrix_list[i] * tm)
        #sp.setMatrix(radius_t_matrix_list[i])
        pm.toggle(sp, localAxis=True)
        