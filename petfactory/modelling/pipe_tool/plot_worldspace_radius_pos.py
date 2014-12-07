import pymel.core as pm
import pprint
import math

#pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)
pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/empty_scene.mb', f=True)

def loc(p, size=.2):
    loc = pm.spaceLocator()
    loc.localScale.set((size,size,size))
    loc.translate.set(p)

def create_profile_points(radius, num_points):
    '''Returns a list of positions (pm.datatypes.Vector) on a circle 
    around the origin, in the xz plane, i.e. y axis as normal'''
    
    ang_inc = (math.pi*2)/num_points
    
    p_list = []
    
    for i in range(num_points):
        u = math.cos(ang_inc*i)*radius
        v = math.sin(ang_inc*i)*radius
        p_list.append(pm.datatypes.Vector(u, 0, v))
     
    return p_list
    
    
def worldspace_radius(cv_list, radius, num_points):
    
    vec_aim = pm.datatypes.Vector(cv_list[0] - cv_list[1]).normal()
    vec_up = pm.datatypes.Vector(cv_list[2] - cv_list[1]).normal()
    pos = pm.datatypes.Vector(cv_list[1])
    
    # construct a orthogonalized coordinate space
    vec_cross = vec_aim.cross(vec_up).normal()
    vec_up_ortho = vec_cross.cross(vec_aim).normal()
    
    # create a transformation matrix
    world_tm = pm.datatypes.TransformationMatrix( [   [vec_aim.x, vec_aim.y, vec_aim.z, 0],
                                                      [vec_up_ortho.x, vec_up_ortho.y, vec_up_ortho.z, 0],   
                                                      [vec_cross.x, vec_cross.y, vec_cross.z, 0],   
                                                      [pos.x, pos.y, pos.z, 1] 
                                                        
                                                    ])
                                                    
    # bring the 3d pos to 2d uv space, by using the dot product to project on the orthogonal "base vectors"
    #aim_u = vec_aim.dot(vec_aim)
    #aim_v = vec_aim.dot(vec_up_ortho)
    
    up_u = vec_up.dot(vec_aim)
    up_v = vec_up.dot(vec_up_ortho)
    
    # using atan2 we can find the angle between the aim vec and the up vector.
    # we have used the dot product to "project" the aim vec so that it is projected
    # on the x axis (the adjacent side in the right angled triangle)
    # we want to get the angle from the adjacent side to the mid vector (mid between the aim and up)
    # that is the reason that multiply it with .5.
    theta = math.atan2(up_v, up_u) * .5
    #radius = 2
    #num_points = 12
    
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
        
    radius_center = pm.datatypes.Vector(adjacent, radius, 0)
    
    # calculate the positions on the circle
    ang_inc = ang_full/(num_points-1)
    
    # the ang from pos x axis to opposite (negative y axis)
    ang_to_opp = (1.5 * math.pi)
    
    t_matrix_list = []
    #transformed_profile_pos = []
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
        t_matrix_list.append(tm * world_tm)
        #loc((p.x, p.y, p.z))
        #transformed_profile_pos.append( [po.rotateBy(tm * world_tm) + p for po in profile_pos] )
        
    return t_matrix_list
    #return transformed_profile_pos


crv = pm.curve(d=1, p=[(10,2,3), (7, 3, 0), (10, 5, -3), (8,12,0), (5,5,0), (0,5,0)])
cv_list = crv.getCVs()
num_cv = len(cv_list)

profile_pos = create_profile_points(.4, 8)

tm_list = worldspace_radius(cv_list=cv_list, radius=3, num_points=9)


result_pos_list = []

for index in range(num_cv-2):
    
    tm_list = worldspace_radius(cv_list=cv_list[index:index+3], radius=1.5, num_points=9)
    
    if index is 0:
        first_matrix = tm_list[0]
    
    
    for tm in tm_list:
            result_pos_list.append([pos.rotateBy(tm) + tm.getTranslation(space='world') for pos in profile_pos])
            
    if index is num_cv-3:
        result_pos_list.insert(0, [pos.rotateBy(first_matrix) + cv_list[0] for pos in profile_pos])
        result_pos_list.append([pos.rotateBy(tm_list[-1]) + cv_list[-1] for pos in profile_pos])
        
                

#pprint.pprint(result_pos_list)
for result_pos in result_pos_list:
    pos_list = result_pos
    
    for pos in pos_list:
        cube = pm.polySphere(r=.06)[0]
        cube.translate.set(pos)
        

