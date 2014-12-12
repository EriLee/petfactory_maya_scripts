import maya.OpenMaya as om
import pymel.core as pm
import pprint
import math

import petfactory.modelling.mesh.extrude_profile as pet_extrude
reload(pet_extrude)

#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/empty_scene.mb', f=True)

def loc(p, size=.2):
    loc = pm.spaceLocator()
    loc.localScale.set((size,size,size))
    loc.translate.set(p)

def dot(p, r=.2, name='mySphere'):
    sp = pm.polySphere(r=r, n=name)[0]
    sp.translate.set(p)
    pm.toggle(sp, localAxis=True)

   
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
    for i in range(num_points):
        
        a = ang_to_opp - (ang_inc * i)
        x = math.cos(a) * radius + adjacent
        y = math.sin(a) * radius + radius
        p = pm.datatypes.Vector(x, y, 0)
        
        # create the etransformation matrix
        aim = (radius_center - p).normal()
        up = pm.datatypes.Vector(0,0,1)
        cross = aim.cross(up)
        
  
        tm = pm.datatypes.TransformationMatrix( [   [cross.x, cross.y, cross.z, 0],
                                                    [aim.x, aim.y, aim.z, 0],
                                                    [up.x, up.y, up.z, 0],
                                                    [p.x, p.y, p.z, 1] ])
        
        t_matrix_list.append(tm * world_tm)
        
    return t_matrix_list



def create_profile_points(radius, num_points):
    '''Returns a list of positions (pm.datatypes.Vector) on a circle 
    around the origin, in the xz plane, i.e. y axis as normal'''
    
    ang_inc = (math.pi*2)/num_points
    
    p_list = []
    
    for i in range(num_points):
        u = math.cos(ang_inc*i)*radius
        v = math.sin(ang_inc*i)*radius
        p_list.append(pm.datatypes.Vector(0, v, u))
     
    return p_list
    
       
# build a transformation matrix list for the start point, all the radius positions and the last point
def create_round_corner_matrix_list(cv_list, num_radius_div):

    num_cv = len(cv_list)
    result_matrix_list = []
    last_matrix = None
    
    print('\n')
    
    
    # all the radius calculations is done when the index is in range 0 - (length-2)
    # I am using the index in the cv positions array [n:n+3] i.e. if the starting 
    # index is 0 I take aslice of the list starting at 0 index up to 3 (but not including)
    # so index 0,1,2 is used to calculate the radie. so we would get and index error if
    # we go past num_cv-2.
    for index in range(num_cv-2):
        
        # calculate the radius
        tm_list = worldspace_radius(cv_list=cv_list[index:index+3], radius=1, num_points=num_radius_div)
        
        # first cv
        if index is 0:
            
            # get the rotation matrix from the first matrix in the tm_list (the first matrix of the radius)
            # set the translation to the world pos of the first cv
            temp_m = pm.datatypes.TransformationMatrix(tm_list[0].asRotateMatrix())
            temp_m.a30 = cv_list[0].x
            temp_m.a31 = cv_list[0].y
            temp_m.a32 = cv_list[0].z
            
            # add the to matrices of the first straight pipe, then add the radius matrix list
            result_matrix_list.append([temp_m, tm_list[0]])
            result_matrix_list.append(tm_list)
            
            last_matrix = tm_list[-1]
        
        # last cv to be used when calculating the radius 
        elif index is num_cv-2:           
            print('LAST radie cv: \n\t> straight\n')
            
        # mid cv, we are betwen the first and last cv
        else:
            
            # get the rotation matrix from the last matrix (prevoius radius)
            # set the translation to the world pos of the the first matrix in the current radius matrix list         
            temp_m = pm.datatypes.TransformationMatrix(last_matrix.asRotateMatrix())
            pos = tm_list[0].getTranslation(space='world')
            temp_m.a30 = pos.x
            temp_m.a31 = pos.y
            temp_m.a32 = pos.z
            
            # add the radius list, then the following straight pipe
            result_matrix_list.append(tm_list)
            result_matrix_list.append([last_matrix, temp_m])
            
            last_matrix = tm_list[-1]
            
 
    # the last cv of the crv, get the ending position of the last straight pipe
    temp_m = pm.datatypes.TransformationMatrix(tm_list[-1].asRotateMatrix())
    temp_m.a30 = cv_list[-1].x
    temp_m.a31 = cv_list[-1].y
    temp_m.a32 = cv_list[-1].z
                
    result_matrix_list.append([tm_list[-1], temp_m])


    return result_matrix_list
        


def transform_profile_list(result_matrix_list, profile_pos): 

    
    result_pos_list = []
    
    for matrix_list in result_matrix_list:
        
        temp_list = []
        for matrix in matrix_list:
            #sp = pm.polySphere(r=.2)[0]
            #sp.setMatrix(matrix)
            #pm.toggle(sp, localAxis=True)
            temp_list.append([pos.rotateBy(matrix) + matrix.getTranslation(space='world') for pos in profile_pos])
            
        result_pos_list.append(temp_list)
            
    return result_pos_list
            

#crv = pm.curve(d=1, p=[(10,2,3), (7, 3, 0), (10, 5, -3), (8,10,3), (5,5,0), (0,5,-3)])
#crv = pm.curve(d=1, p=[(10, -5, 0), (0,0,0), (10, 5, 0)])
#crv = pm.curve(d=1, p=[(10, -5, 0), (0,0,0), (10, 5, 0), (10,10,0), (0,10,0)])

crv = pm.ls(sl=True)[0]
cv_list = crv.getCVs(space='world')

# get the matrix list
result_matrix_list = create_round_corner_matrix_list(cv_list, num_radius_div=10)

# create the profile 
profile_pos = create_profile_points(radius=.4, num_points=12)

# get the positions
pos_list = transform_profile_list(result_matrix_list=result_matrix_list, profile_pos=profile_pos)


def build_mesh(pos_list):
    
    mesh_list = []
    for p in pos_list:
        mesh_list.append(pet_extrude.mesh_from_pos_list(pos_list=p, name='test'))
    return mesh_list

mesh_list = build_mesh(pos_list)
