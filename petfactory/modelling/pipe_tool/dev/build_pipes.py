import pymel.core as pm
import pprint
import math

#pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)
#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/empty_scene.mb', f=True)
#pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)


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


    
 
# visualize
'''
num_mid_points = 1
u_inc = 1.0 / (num_mid_points+1)

for index, result_matrix in enumerate(result_matrix_list):
   
    for matrix in result_matrix:
        sp = pm.polySphere(r=.10)[0]
        pm.toggle(sp, localAxis=True)
        sp.setMatrix(matrix)
        
    if index > 0:

        end_pos = result_matrix[0].getTranslation(space='world')
        
        #dot(start_pos, name='start_pos_{0}'.format(index))
        #dot(end_pos, name='end_pos_{0}'.format(index))
        
        for n in range( num_mid_points):
            
            mid_pos = (end_pos - start_pos)*(n+1)*u_inc + start_pos
        
            dot(mid_pos, r=.1,  name='smid_pos_{0}'.format(index))
        
        
    start_pos = result_matrix[-1].getTranslation(space='world')
'''    
    

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
    for index in range(num_cv):
    
        if index <num_cv-2:
            
            tm_list = worldspace_radius(cv_list=cv_list[index:index+3], radius=1, num_points=num_radius_div)
            
            # if we are at the first cv, copy the transformation matrix of the first radius,
            # and set the translation to the cv pos
            if index is 0:
                
                temp_m = pm.datatypes.TransformationMatrix(tm_list[0].asRotateMatrix())
                temp_m.a30 = cv_list[0].x
                temp_m.a31 = cv_list[0].y
                temp_m.a32 = cv_list[0].z
                
                result_matrix_list.append([temp_m])
                
            result_matrix_list.append(tm_list)
           
        # we are at the last cv, copy the last transformation matrix in the matrix list,
        # of the last corner set the translation to the position of the last cv 
        elif index is num_cv-1:
    
            temp_m = pm.datatypes.TransformationMatrix(tm_list[-1].asRotateMatrix())
            temp_m.a30 = cv_list[-1].x
            temp_m.a31 = cv_list[-1].y
            temp_m.a32 = cv_list[-1].z
            
            result_matrix_list.append([temp_m])
            
    return result_matrix_list
        

def plot_profile_from_matrix_list(result_matrix_list, profile_pos): 

    result_pos_list = []
    for result_matrix in result_matrix_list:
       
        for matrix in result_matrix:
            result_pos_list.append([pos.rotateBy(matrix) + matrix.getTranslation(space='world') for pos in profile_pos])

    for result_pos in result_pos_list:
    
        for pos in result_pos:
            cube = pm.polySphere(r=.06)[0]
            cube.translate.set(pos)      
 


def add_pipe_fitting(matrix_list):
    
    num_cv = len(result_matrix_list)

    for index, matrix in enumerate(matrix_list):
         
        if index is 0:
            print('first', index)
            cube = pm.polyCube()[0]
            cube.setMatrix(matrix[0])
            
        elif index is num_cv-1:
            print('last', index)
            cube = pm.polyCube()[0]
            cube.setMatrix(matrix[0])
   
        else:
            print('mid', index)
            cube = pm.polyCube()[0]
            cube.setMatrix(matrix[0])
            
            cube = pm.polyCube()[0]
            cube.setMatrix(matrix[-1])
                


def build_mesh_slow(result_matrix_list, profile_pos): 

    result_pos_list = []
    for result_matrix in result_matrix_list:
        
        for matrix in result_matrix:
            result_pos_list.append([pos.rotateBy(matrix) + matrix.getTranslation(space='world') for pos in profile_pos])

    num_sections = len(result_pos_list)
    num_faces = len(result_pos_list[0])
    
    #print(num_sections)
    #print(num_faces)
    
    #polygon_list = []
    for i, result_pos in enumerate(result_pos_list):
        
        polygon_list = []
        
        if i < num_sections-1:
            
            #polygon_list = []
            
            for j, pos in enumerate(result_pos):
                                
                if j < num_faces-1:
                
                    p_list = [result_pos_list[i][j], result_pos_list[i][j+1], result_pos_list[i+1][j+1], result_pos_list[i+1][j]]
                
                else:
                    p_list = [result_pos_list[i][j], result_pos_list[i][0], result_pos_list[i+1][0], result_pos_list[i+1][j]]
   
                polygon = pm.polyCreateFacet(p=p_list, name='face_{0}_{1}'.format(i, j))[0]
                polygon_list.append(polygon)
            '''    
            try:
                mesh = pm.polyUnite(polygon_list, ch=False)
                pm.polyMergeVertex(mesh, d=0.05)
                pm.delete(mesh, ch=True)
                
            except RuntimeError as e:
                print e
        
            '''


        if len(polygon_list) > 1:
            try:
                print('merging')
                mesh = pm.polyUnite(polygon_list, ch=False)
                pm.polyMergeVertex(mesh, d=0.05)
                pm.delete(mesh, ch=True)
                
            except RuntimeError as e:
                print e
                

                
    #mesh = pm.polyUnite(polygon_list, ch=False)
    #pm.polyMergeVertex(mesh, d=0.01)
    #pm.delete(mesh, ch=True)
            


#crv = pm.curve(d=1, p=[(10,2,3), (7, 3, 0), (10, 5, -3), (8,10,3), (5,5,0), (0,5,-3)])
#crv = pm.curve(d=1, p=[(10, -5, 0), (0,0,0), (10, 5, 0)])

crv = pm.ls(sl=True)[0]
cv_list = crv.getCVs()

# get the matrix list
result_matrix_list = create_round_corner_matrix_list(cv_list, num_radius_div=10)

# cretae the profile 
profile_pos = create_profile_points(radius=.4, num_points=12)

# plot the profile with the matrix list
#plot_profile_from_matrix_list(result_matrix_list, profile_pos)

# add fitting mesh to each radius to liner connection
#add_pipe_fitting(result_matrix_list)


build_mesh_slow(result_matrix_list, profile_pos)




