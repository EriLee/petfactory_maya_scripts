from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
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
    

def add_division_to_straight_pipe(start_matrix, end_matrix, num_divisions):
    
    ret_matrix_list = []
    
    start_pos = start_matrix.getTranslation(space='world')
    end_pos = end_matrix.getTranslation(space='world')
    
    vec = end_pos - start_pos
    inc = 1.0/(num_divisions-1)
    
    for i in range(num_divisions):
        
        temp_m = pm.datatypes.TransformationMatrix(start_matrix.asRotateMatrix())
        pos = start_pos+vec*i*inc
        temp_m.a30 = pos.x
        temp_m.a31 = pos.y
        temp_m.a32 = pos.z
        ret_matrix_list.append(temp_m)

    return ret_matrix_list
           
# build a transformation matrix list for the start point, all the radius positions and the last point
def create_round_corner_matrix_list(cv_list, radius_list, radial_divisions, length_divisions):

    num_cv = len(cv_list)
    
    if len(cv_list)-2 != len(radius_list):
        print('apa')
        return None
    
    result_matrix_list = []
    last_matrix = None
    
    # all the radius calculations is done when the index is in range 0 - (length-2)
    # I am using the index in the cv positions array [n:n+3] i.e. if the starting 
    # index is 0 I take aslice of the list starting at 0 index up to 3 (but not including)
    # so index 0,1,2 is used to calculate the radie. so we would get and index error if
    # we go past num_cv-2.
    for index in range(num_cv-2):
        
        # calculate the radius
        tm_list = worldspace_radius(cv_list=cv_list[index:index+3], radius=radius_list[index], num_points=radial_divisions)
        
        # first cv
        if index is 0:
            
            # get the rotation matrix from the first matrix in the tm_list (the first matrix of the radius)
            # set the translation to the world pos of the first cv
            temp_m = pm.datatypes.TransformationMatrix(tm_list[0].asRotateMatrix())
            temp_m.a30 = cv_list[0].x
            temp_m.a31 = cv_list[0].y
            temp_m.a32 = cv_list[0].z
            
            # add the to matrices of the first straight pipe, then add the radius matrix list
            result_matrix_list.append(add_division_to_straight_pipe(temp_m, tm_list[0], length_divisions))
            result_matrix_list.append(tm_list)
            
            last_matrix = tm_list[-1]

          
        # mid cvs
        else:

            # get the rotation matrix from the last matrix (prevoius radius)
            # set the translation to the world pos of the the first matrix in the current radius matrix list         
            temp_m = pm.datatypes.TransformationMatrix(last_matrix.asRotateMatrix())
            pos = tm_list[0].getTranslation(space='world')
            temp_m.a30 = pos.x
            temp_m.a31 = pos.y
            temp_m.a32 = pos.z
            
            # add the radius list, then the following straight pipe
            result_matrix_list.append(add_division_to_straight_pipe(last_matrix, temp_m, length_divisions))
            result_matrix_list.append(tm_list)
            
            last_matrix = tm_list[-1]
            
 
    # the last cv of the crv, get the ending position of the last straight pipe
    temp_m = pm.datatypes.TransformationMatrix(tm_list[-1].asRotateMatrix())
    temp_m.a30 = cv_list[-1].x
    temp_m.a31 = cv_list[-1].y
    temp_m.a32 = cv_list[-1].z
                
    result_matrix_list.append(add_division_to_straight_pipe(tm_list[-1], temp_m, length_divisions))


    return result_matrix_list
        


def transform_profile_list(result_matrix_list, profile_pos): 
   
    result_pos_list = []
    
    for matrix_list in result_matrix_list:
        
        temp_list = []
        for matrix in matrix_list:
            temp_list.append([pos.rotateBy(matrix) + matrix.getTranslation(space='world') for pos in profile_pos])
            
        result_pos_list.append(temp_list)
            
    return result_pos_list
           

def build_mesh(pos_list):
    
    mesh_list = []
    for p in pos_list:
        mesh_list.append(pet_extrude.mesh_from_pos_list(pos_list=p, name='test'))
    return mesh_list


def add_pipe_fitting(result_matrix_list, mesh=None):
    
    if not isinstance(mesh, pm.nodetypes.Transform):
        pm.warning('fitting mesh not a vaild Transform, will use default')
        mesh = None

    mesh_list = []
    for index, matrix_list in enumerate(result_matrix_list):
        
        # just get the matrix list on even index, i.e. the straight pipes
        if not index%2:

            if mesh:
                mesh_1 = pm.duplicate(mesh)[0]
                mesh_2 = pm.duplicate(mesh)[0]
            else:
                mesh_1 = pm.polyCylinder(r=.50, h=.3, axis=(1,0,0))[0]
                mesh_2 = pm.duplicate(mesh_1)[0]
                
                
            mesh_1.setMatrix(matrix_list[0])
            #pm.toggle(mesh_1, localAxis=True)
            
            # flip the rotation of the second pipe fitting
            tm = matrix_list[-1]
            tm.addRotation((0,0,math.pi), order=1, space='preTransform')
            
            mesh_2.setMatrix(tm)
            #pm.toggle(mesh_2, localAxis=True)
            mesh_list.extend([mesh_1, mesh_2])
            
    return mesh_list
            

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


# add pipe image resource
qt_resource_data = "\x00\x00E\xc0\x89PNG\x0d\x0a\x1a\x0a\x00\x00\x00\x0dIHDR\x00\x00\x00 \x00\x00\x00 \x08\x06\x00\x00\x00szz\xf4\x00\x00\x00\x09pHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x0aOiCCPPhotoshop ICC profile\x00\x00x\xda\x9dSgTS\xe9\x16=\xf7\xde\xf4BK\x88\x80\x94KoR\x15\x08 RB\x8b\x80\x14\x91&*!\x09\x10J\x88!\xa1\xd9\x15Q\xc1\x11EE\x04\x1b\xc8\xa0\x88\x03\x8e\x8e\x80\x8c\x15Q,\x0c\x8a\x0a\xd8\x07\xe4!\xa2\x8e\x83\xa3\x88\x8a\xca\xfb\xe1{\xa3k\xd6\xbc\xf7\xe6\xcd\xfe\xb5\xd7>\xe7\xac\xf3\x9d\xb3\xcf\x07\xc0\x08\x0c\x96H3Q5\x80\x0c\xa9B\x1e\x11\xe0\x83\xc7\xc4\xc6\xe1\xe4.@\x81\x0a$p\x00\x10\x08\xb3d!s\xfd#\x01\x00\xf8~<<+\x22\xc0\x07\xbe\x00\x01x\xd3\x0b\x08\x00\xc0M\x9b\xc00\x1c\x87\xff\x0f\xeaB\x99\x5c\x01\x80\x84\x01\xc0t\x918K\x08\x80\x14\x00@z\x8eB\xa6\x00@F\x01\x80\x9d\x98&S\x00\xa0\x04\x00`\xcbcb\xe3\x00P-\x00`'\x7f\xe6\xd3\x00\x80\x9d\xf8\x99{\x01\x00[\x94!\x15\x01\xa0\x91\x00 \x13e\x88D\x00h;\x00\xac\xcfV\x8aE\x00X0\x00\x14fK\xc49\x00\xd8-\x000IWfH\x00\xb0\xb7\x00\xc0\xce\x10\x0b\xb2\x00\x08\x0c\x000Q\x88\x85)\x00\x04{\x00`\xc8##x\x00\x84\x99\x00\x14F\xf2W<\xf1+\xae\x10\xe7*\x00\x00x\x99\xb2<\xb9$9E\x81[\x08-q\x07WW.\x1e(\xceI\x17+\x146a\x02a\x9a@.\xc2y\x99\x192\x814\x0f\xe0\xf3\xcc\x00\x00\xa0\x91\x15\x11\xe0\x83\xf3\xfdx\xce\x0e\xae\xce\xce6\x8e\xb6\x0e_-\xea\xbf\x06\xff\x22bb\xe3\xfe\xe5\xcf\xabp@\x00\x00\xe1t~\xd1\xfe,/\xb3\x1a\x80;\x06\x80m\xfe\xa2%\xee\x04h^\x0b\xa0u\xf7\x8bf\xb2\x0f@\xb5\x00\xa0\xe9\xdaW\xf3p\xf8~<<E\xa1\x90\xb9\xd9\xd9\xe5\xe4\xe4\xd8J\xc4B[a\xcaW}\xfeg\xc2_\xc0W\xfdl\xf9~<\xfc\xf7\xf5\xe0\xbe\xe2$\x812]\x81G\x04\xf8\xe0\xc2\xcc\xf4L\xa5\x1c\xcf\x92\x09\x84b\xdc\xe6\x8fG\xfc\xb7\x0b\xff\xfc\x1d\xd3\x22\xc4Ib\xb9X*\x14\xe3Q\x12q\x8eD\x9a\x8c\xf32\xa5\x22\x89B\x92)\xc5%\xd2\xffd\xe2\xdf,\xfb\x03>\xdf5\x00\xb0j>\x01{\x91-\xa8]c\x03\xf6K'\x10Xt\xc0\xe2\xf7\x00\x00\xf2\xbbo\xc1\xd4(\x08\x03\x80h\x83\xe1\xcfw\xff\xef?\xfdG\xa0%\x00\x80fI\x92q\x00\x00^D$.T\xca\xb3?\xc7\x08\x00\x00D\xa0\x81*\xb0A\x1b\xf4\xc1\x18,\xc0\x06\x1c\xc1\x05\xdc\xc1\x0b\xfc`6\x84B$\xc4\xc2B\x10B\x0ad\x80\x1cr`)\xac\x82B(\x86\xcd\xb0\x1d*`/\xd4@\x1d4\xc0Qh\x86\x93p\x0e.\xc2U\xb8\x0e=p\x0f\xfaa\x08\x9e\xc1(\xbc\x81\x09\x04A\xc8\x08\x13a!\xda\x88\x01b\x8aX#\x8e\x08\x17\x99\x85\xf8!\xc1H\x04\x12\x8b$ \xc9\x88\x14Q\x22K\x915H1R\x8aT UH\x1d\xf2=r\x029\x87\x5cF\xba\x91;\xc8\x002\x82\xfc\x86\xbcG1\x94\x81\xb2Q=\xd4\x0c\xb5C\xb9\xa87\x1a\x84F\xa2\x0b\xd0dt1\x9a\x8f\x16\xa0\x9b\xd0r\xb4\x1a=\x8c6\xa1\xe7\xd0\xabh\x0f\xda\x8f>C\xc70\xc0\xe8\x18\x073\xc4l0.\xc6\xc3B\xb18,\x09\x93c\xcb\xb1\x22\xac\x0c\xab\xc6\x1a\xb0V\xac\x03\xbb\x89\xf5c\xcf\xb1w\x04\x12\x81E\xc0\x096\x04wB a\x1eAHXLXN\xd8H\xa8 \x1c$4\x11\xda\x097\x09\x03\x84Q\xc2'\x22\x93\xa8K\xb4&\xba\x11\xf9\xc4\x18b21\x87XH,#\xd6\x12\x8f\x13/\x10{\x88C\xc47$\x12\x89C2'\xb9\x90\x02I\xb1\xa4T\xd2\x12\xd2F\xd2nR#\xe9,\xa9\x9b4H\x1a#\x93\xc9\xdadk\xb2\x079\x94, +\xc8\x85\xe4\x9d\xe4\xc3\xe43\xe4\x1b\xe4!\xf2[\x0a\x9db@q\xa4\xf8S\xe2(R\xcajJ\x19\xe5\x10\xe54\xe5\x06e\x982AU\xa3\x9aR\xdd\xa8\xa1T\x115\x8fZB\xad\xa1\xb6R\xafQ\x87\xa8\x134u\x9a9\xcd\x83\x16IK\xa5\xad\xa2\x95\xd3\x1ah\x17h\xf7i\xaf\xe8t\xba\x11\xdd\x95\x1eN\x97\xd0W\xd2\xcb\xe9G\xe8\x97\xe8\x03\xf4w\x0c\x0d\x86\x15\x83\xc7\x88g(\x19\x9b\x18\x07\x18g\x19w\x18\xaf\x98L\xa6\x19\xd3\x8b\x19\xc7T071\xeb\x98\xe7\x99\x0f\x99oUX*\xb6*|\x15\x91\xca\x0a\x95J\x95&\x95\x1b*/T\xa9\xaa\xa6\xaa\xde\xaa\x0bU\xf3U\xcbT\x8f\xa9^S}\xaeFU3S\xe3\xa9\x09\xd4\x96\xabU\xaa\x9dP\xebS\x1bSg\xa9;\xa8\x87\xaag\xa8oT?\xa4~Y\xfd\x89\x06Y\xc3L\xc3OC\xa4Q\xa0\xb1_\xe3\xbc\xc6 \x0bc\x19\xb3x,!k\x0d\xab\x86u\x815\xc4&\xb1\xcd\xd9|v*\xbb\x98\xfd\x1d\xbb\x8b=\xaa\xa9\xa19C3J3W\xb3R\xf3\x94f?\x07\xe3\x98q\xf8\x9ctN\x09\xe7(\xa7\x97\xf3~\x8a\xde\x14\xef)\xe2)\x1b\xa64L\xb91e\x5ck\xaa\x96\x97\x96X\xabH\xabQ\xabG\xeb\xbd6\xae\xed\xa7\x9d\xa6\xbdE\xbbY\xfb\x81\x0eA\xc7J'\x5c'Gg\x8f\xce\x05\x9d\xe7S\xd9S\xdd\xa7\x0a\xa7\x16M=:\xf5\xae.\xaak\xa5\x1b\xa1\xbbDw\xbfn\xa7\xee\x98\x9e\xbe^\x80\x9eLo\xa7\xdey\xbd\xe7\xfa\x1c}/\xfdT\xfdm\xfa\xa7\xf5G\x0cX\x06\xb3\x0c$\x06\xdb\x0c\xce\x18<\xc55qo<\x1d/\xc7\xdb\xf1QC]\xc3@C\xa5a\x95a\x97\xe1\x84\x91\xb9\xd1<\xa3\xd5F\x8dF\x0f\x8ci\xc6\x5c\xe3$\xe3m\xc6m\xc6\xa3&\x06&!&KM\xeaM\xee\x9aRM\xb9\xa6)\xa6;L;L\xc7\xcd\xcc\xcd\xa2\xcd\xd6\x995\x9b=1\xd72\xe7\x9b\xe7\x9b\xd7\x9b\xdf\xb7`ZxZ,\xb6\xa8\xb6\xb8eI\xb2\xe4Z\xa6Y\xee\xb6\xbcn\x85Z9Y\xa5XUZ]\xb3F\xad\x9d\xad%\xd6\xbb\xad\xbb\xa7\x11\xa7\xb9N\x93N\xab\x9e\xd6g\xc3\xb0\xf1\xb6\xc9\xb6\xa9\xb7\x19\xb0\xe5\xd8\x06\xdb\xae\xb6m\xb6}agb\x17g\xb7\xc5\xae\xc3\xee\x93\xbd\x93}\xba}\x8d\xfd=\x07\x0d\x87\xd9\x0e\xab\x1dZ\x1d~s\xb4r\x14:V:\xde\x9a\xce\x9c\xee?}\xc5\xf4\x96\xe9/gX\xcf\x10\xcf\xd83\xe3\xb6\x13\xcb)\xc4i\x9dS\x9b\xd3Gg\x17g\xb9s\x83\xf3\x88\x8b\x89K\x82\xcb.\x97>.\x9b\x1b\xc6\xdd\xc8\xbd\xe4Jt\xf5q]\xe1z\xd2\xf5\x9d\x9b\xb3\x9b\xc2\xed\xa8\xdb\xaf\xee6\xeei\xee\x87\xdc\x9f\xcc4\x9f)\x9eY3s\xd0\xc3\xc8C\xe0Q\xe5\xd1?\x0b\x9f\x950k\xdf\xac~OCO\x81g\xb5\xe7#/c/\x91W\xad\xd7\xb0\xb7\xa5w\xaa\xf7a\xef\x17>\xf6>r\x9f\xe3>\xe3<7\xde2\xdeY_\xcc7\xc0\xb7\xc8\xb7\xcbO\xc3o\x9e_\x85\xdfC\x7f#\xffd\xffz\xff\xd1\x00\xa7\x80%\x01g\x03\x89\x81A\x81[\x02\xfb\xf8z|!\xbf\x8e?:\xdbe\xf6\xb2\xd9\xedA\x8c\xa0\xb9A\x15A\x8f\x82\xad\x82\xe5\xc1\xad!h\xc8\xec\x90\xad!\xf7\xe7\x98\xce\x91\xcei\x0e\x85P~\xe8\xd6\xd0\x07a\xe6a\x8b\xc3~\x0c'\x85\x87\x85W\x86?\x8ep\x88X\x1a\xd11\x975w\xd1\xdcCs\xdfD\xfaD\x96D\xde\x9bg1O9\xaf-J5*>\xaa.j<\xda7\xba4\xba?\xc6.fY\xcc\xd5X\x9dXIlK\x1c9.*\xae6nl\xbe\xdf\xfc\xed\xf3\x87\xe2\x9d\xe2\x0b\xe3{\x17\x98/\xc8]py\xa1\xce\xc2\xf4\x85\xa7\x16\xa9.\x12,:\x96@L\x88N8\x94\xf0A\x10*\xa8\x16\x8c%\xf2\x13w%\x8e\x0ay\xc2\x1d\xc2g\x22/\xd16\xd1\x88\xd8C\x5c*\x1eN\xf2H*Mz\x92\xec\x91\xbc5y$\xc53\xa5,\xe5\xb9\x84'\xa9\x90\xbcL\x0dL\xdd\x9b:\x9e\x16\x9av m2=:\xbd1\x83\x92\x91\x90qB\xaa!M\x93\xb6g\xeag\xe6fv\xcb\xace\x85\xb2\xfe\xc5n\x8b\xb7/\x1e\x95\x07\xc9k\xb3\x90\xac\x05Y-\x0a\xb6B\xa6\xe8TZ(\xd7*\x07\xb2geWf\xbf\xcd\x89\xca9\x96\xab\x9e+\xcd\xed\xcc\xb3\xca\xdb\x907\x9c\xef\x9f\xff\xed\x12\xc2\x12\xe1\x92\xb6\xa5\x86KW-\x1dX\xe6\xbd\xacj9\xb2<qy\xdb\x0a\xe3\x15\x05+\x86V\x06\xac<\xb8\x8a\xb6*m\xd5O\xab\xedW\x97\xae~\xbd&zMk\x81^\xc1\xca\x82\xc1\xb5\x01k\xeb\x0bU\x0a\xe5\x85}\xeb\xdc\xd7\xed]OX/Y\xdf\xb5a\xfa\x86\x9d\x1b>\x15\x89\x8a\xae\x14\xdb\x17\x97\x15\x7f\xd8(\xdcx\xe5\x1b\x87o\xca\xbf\x99\xdc\x94\xb4\xa9\xab\xc4\xb9d\xcff\xd2f\xe9\xe6\xde-\x9e[\x0e\x96\xaa\x97\xe6\x97\x0en\x0d\xd9\xda\xb4\x0d\xdfV\xb4\xed\xf5\xf6E\xdb/\x97\xcd(\xdb\xbb\x83\xb6C\xb9\xa3\xbf<\xb8\xbce\xa7\xc9\xce\xcd;?T\xa4T\xf4T\xfaT6\xee\xd2\xdd\xb5a\xd7\xf8n\xd1\xee\x1b{\xbc\xf64\xec\xd5\xdb[\xbc\xf7\xfd>\xc9\xbe\xdbU\x01UM\xd5f\xd5e\xfbI\xfb\xb3\xf7?\xae\x89\xaa\xe9\xf8\x96\xfbm]\xadNmq\xed\xc7\x03\xd2\x03\xfd\x07#\x0e\xb6\xd7\xb9\xd4\xd5\x1d\xd2=TR\x8f\xd6+\xebG\x0e\xc7\x1f\xbe\xfe\x9d\xefw-\x0d6\x0dU\x8d\x9c\xc6\xe2#pDy\xe4\xe9\xf7\x09\xdf\xf7\x1e\x0d:\xdav\x8c{\xac\xe1\x07\xd3\x1fv\x1dg\x1d/jB\x9a\xf2\x9aF\x9bS\x9a\xfb[b[\xbaO\xcc>\xd1\xd6\xea\xdez\xfcG\xdb\x1f\x0f\x9c4<YyJ\xf3T\xc9i\xda\xe9\x82\xd3\x93g\xf2\xcf\x8c\x9d\x95\x9d}~.\xf9\xdc`\xdb\xa2\xb6{\xe7c\xce\xdfj\x0fo\xef\xba\x10t\xe1\xd2E\xff\x8b\xe7;\xbc;\xce\x5c\xf2\xb8t\xf2\xb2\xdb\xe5\x13W\xb8W\x9a\xaf:_m\xeat\xea<\xfe\x93\xd3O\xc7\xbb\x9c\xbb\x9a\xae\xb9\x5ck\xb9\xeez\xbd\xb5{f\xf7\xe9\x1b\x9e7\xce\xdd\xf4\xbdy\xf1\x16\xff\xd6\xd5\x9e9=\xdd\xbd\xf3zo\xf7\xc5\xf7\xf5\xdf\x16\xdd~r'\xfd\xce\xcb\xbb\xd9w'\xee\xad\xbcO\xbc_\xf4@\xedA\xd9C\xdd\x87\xd5?[\xfe\xdc\xd8\xef\xdc\x7fj\xc0w\xa0\xf3\xd1\xdcG\xf7\x06\x85\x83\xcf\xfe\x91\xf5\x8f\x0fC\x05\x8f\x99\x8f\xcb\x86\x0d\x86\xeb\x9e8>99\xe2?r\xfd\xe9\xfc\xa7C\xcfd\xcf&\x9e\x17\xfe\xa2\xfe\xcb\xae\x17\x16/~\xf8\xd5\xeb\xd7\xce\xd1\x98\xd1\xa1\x97\xf2\x97\x93\xbfm|\xa5\xfd\xea\xc0\xeb\x19\xaf\xdb\xc6\xc2\xc6\x1e\xbe\xc9x31^\xf4V\xfb\xed\xc1w\xdcw\x1d\xef\xa3\xdf\x0fO\xe4| \x7f(\xffh\xf9\xb1\xf5S\xd0\xa7\xfb\x93\x19\x93\x93\xff\x04\x03\x98\xf3\xfcc3-\xdb\x00\x00:6iTXtXML:com.adobe.xmp\x00\x00\x00\x00\x00<?xpacket begin=\x22\xef\xbb\xbf\x22 id=\x22W5M0MpCehiHzreSzNTczkc9d\x22?>\x0a<x:xmpmeta xmlns:x=\x22adobe:ns:meta/\x22 x:xmptk=\x22Adobe XMP Core 5.5-c021 79.155772, 2014/01/13-19:44:00        \x22>\x0a   <rdf:RDF xmlns:rdf=\x22http://www.w3.org/1999/02/22-rdf-syntax-ns#\x22>\x0a      <rdf:Description rdf:about=\x22\x22\x0a            xmlns:xmp=\x22http://ns.adobe.com/xap/1.0/\x22\x0a            xmlns:xmpMM=\x22http://ns.adobe.com/xap/1.0/mm/\x22\x0a            xmlns:stEvt=\x22http://ns.adobe.com/xap/1.0/sType/ResourceEvent#\x22\x0a            xmlns:dc=\x22http://purl.org/dc/elements/1.1/\x22\x0a            xmlns:photoshop=\x22http://ns.adobe.com/photoshop/1.0/\x22\x0a            xmlns:tiff=\x22http://ns.adobe.com/tiff/1.0/\x22\x0a            xmlns:exif=\x22http://ns.adobe.com/exif/1.0/\x22>\x0a         <xmp:CreatorTool>Adobe Photoshop CC 2014 (Macintosh)</xmp:CreatorTool>\x0a         <xmp:CreateDate>2014-12-12T16:47:57+01:00</xmp:CreateDate>\x0a         <xmp:MetadataDate>2014-12-12T16:47:57+01:00</xmp:MetadataDate>\x0a         <xmp:ModifyDate>2014-12-12T16:47:57+01:00</xmp:ModifyDate>\x0a         <xmpMM:InstanceID>xmp.iid:737c48af-e244-40a6-8217-017c532f444d</xmpMM:InstanceID>\x0a         <xmpMM:DocumentID>adobe:docid:photoshop:a273596f-c2a4-1177-a4de-8625a4148d4b</xmpMM:DocumentID>\x0a         <xmpMM:OriginalDocumentID>xmp.did:18954f80-cec1-47ab-82ea-7cb65cd21ed0</xmpMM:OriginalDocumentID>\x0a         <xmpMM:History>\x0a            <rdf:Seq>\x0a               <rdf:li rdf:parseType=\x22Resource\x22>\x0a                  <stEvt:action>created</stEvt:action>\x0a                  <stEvt:instanceID>xmp.iid:18954f80-cec1-47ab-82ea-7cb65cd21ed0</stEvt:instanceID>\x0a                  <stEvt:when>2014-12-12T16:47:57+01:00</stEvt:when>\x0a                  <stEvt:softwareAgent>Adobe Photoshop CC 2014 (Macintosh)</stEvt:softwareAgent>\x0a               </rdf:li>\x0a               <rdf:li rdf:parseType=\x22Resource\x22>\x0a                  <stEvt:action>saved</stEvt:action>\x0a                  <stEvt:instanceID>xmp.iid:737c48af-e244-40a6-8217-017c532f444d</stEvt:instanceID>\x0a                  <stEvt:when>2014-12-12T16:47:57+01:00</stEvt:when>\x0a                  <stEvt:softwareAgent>Adobe Photoshop CC 2014 (Macintosh)</stEvt:softwareAgent>\x0a                  <stEvt:changed>/</stEvt:changed>\x0a               </rdf:li>\x0a            </rdf:Seq>\x0a         </xmpMM:History>\x0a         <dc:format>image/png</dc:format>\x0a         <photoshop:ColorMode>3</photoshop:ColorMode>\x0a         <photoshop:ICCProfile>sRGB IEC61966-2.1</photoshop:ICCProfile>\x0a         <tiff:Orientation>1</tiff:Orientation>\x0a         <tiff:XResolution>720000/10000</tiff:XResolution>\x0a         <tiff:YResolution>720000/10000</tiff:YResolution>\x0a         <tiff:ResolutionUnit>2</tiff:ResolutionUnit>\x0a         <exif:ColorSpace>1</exif:ColorSpace>\x0a         <exif:PixelXDimension>32</exif:PixelXDimension>\x0a         <exif:PixelYDimension>32</exif:PixelYDimension>\x0a      </rdf:Description>\x0a   </rdf:RDF>\x0a</x:xmpmeta>\x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                                                                                                    \x0a                            \x0a<?xpacket end=\x22w\x22?>\x7f\xba}<\x00\x00\x00 cHRM\x00\x00z%\x00\x00\x80\x83\x00\x00\xf9\xff\x00\x00\x80\xe9\x00\x00u0\x00\x00\xea`\x00\x00:\x98\x00\x00\x17o\x92_\xc5F\x00\x00\x00\xa9IDATx\xdabdaa\xf9\xcf0\x80\x80\x85\x81\x81\x81a\xc1\x8e?\x03by\x82\x07\x0b\xc4\x01\x15'D0$;,\xde`\xd5\x84M-\xf9\xe0\x03\x03\x13\xcc2\x18&\x06\x90\xa2\x16\xd93\xc84\x8c\xcdD\x8f\xa0\xae8!\xc2\xd0a\xf1\x06N#\x03\xba8\x00\xd9r\xf4(\x1c\x0d\x81\xd1\x10\x18\x0d\x81\xd1\x10`\x1c\xe8\xda\x90\xf1?\x03\xc4~V\x16V\xba:\xe4\xf7\x9f\xdf\x8c\xf0\xea\x18\x06\x90\xabeXPa\xabt\x90\xe3\x92P\xed\x88-\xee\x13<X\xe8\x97\x06p\xc5=\xdd\x1c\x80+\xf5\x8f\x86\xc0h\x08\x8c\x86\xc0h\x08\x8c\x86\xc0h\x08\x0c\x9a\x10\x00\x0c\x00\xf8\x8d\xad\xfc]\x9f\xceP\x00\x00\x00\x00IEND\xaeB`\x82"
qt_resource_name = "\x00\x05\x00p7\xd5\x00i\x00m\x00a\x00g\x00e"
qt_resource_struct = "\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00"
def qInitResources():
    QtCore.qRegisterResourceData(0x01, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x01, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()




# the main ui class  
class Curve_spreadsheet(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(Curve_spreadsheet, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300, 350)
        self.setWindowTitle("Pipe Tool")
                
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        

        # add path
        self.path_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.path_horiz_layout)
              
        self.add_path_button = QtGui.QPushButton('Add Path')
        self.add_path_button.setMinimumWidth(75)
        self.path_horiz_layout.addWidget(self.add_path_button)
        self.add_path_button.clicked.connect(self.add_path_click)
        
        self.path_line_edit = QtGui.QLineEdit()
        self.path_horiz_layout.addWidget(self.path_line_edit)
        
        # add mesh
        self.fitting_mesh_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.fitting_mesh_horiz_layout)
               
        self.add_fitting_mesh_button = QtGui.QPushButton('Add Mesh')
        self.add_fitting_mesh_button.setMinimumWidth(75)
        self.fitting_mesh_horiz_layout.addWidget(self.add_fitting_mesh_button)
        self.add_fitting_mesh_button.clicked.connect(self.add_fitting_mesh_click)
        
        self.fitting_mesh_line_edit = QtGui.QLineEdit()
        self.fitting_mesh_horiz_layout.addWidget(self.fitting_mesh_line_edit)
        
        
        # table view  
        self.table_view = QtGui.QTableView()
        self.vertical_layout.addWidget(self.table_view)
        
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Radius'])
  
        self.table_view.setModel(self.model)
        
        #v_header = self.table_view.verticalHeader()
        h_header = self.table_view.horizontalHeader()
        h_header.setResizeMode(QtGui.QHeaderView.Stretch)
        
        self.pipe_radius_spinbox = Curve_spreadsheet.add_int_spinbox('Pipe radius', self.vertical_layout)
        self.axis_div_spinbox = Curve_spreadsheet.add_int_spinbox('Axis Divisions', self.vertical_layout)
        self.length_div_spinbox = Curve_spreadsheet.add_int_spinbox('Length Divisions', self.vertical_layout)
        self.radial_div_spinbox = Curve_spreadsheet.add_int_spinbox('Radial Divisions', self.vertical_layout)
                
        # build button
        self.build_button_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.build_button_horiz_layout)
        
        # create an icon from the resource
        icon = QtGui.QIcon(QtGui.QPixmap(":image"))
        button = QtGui.QPushButton(icon, 'pos x')

        self.build_button_horiz_layout.addStretch()
        self.build_button = QtGui.QPushButton(icon, 'Warp Pipe!')
        self.build_button.setMinimumWidth(100)
        self.build_button_horiz_layout.addWidget(self.build_button)
        self.build_button.clicked.connect(self.on_build_click)
    
    
    @staticmethod
    def add_int_spinbox(label, parent_layout):
        
        horiz_layout = QtGui.QHBoxLayout()
        parent_layout.addLayout(horiz_layout)

        label = QtGui.QLabel(label)
        label.setMinimumWidth(100)
        horiz_layout.addWidget(label)
        
        horiz_layout.addStretch()
         
        spinbox = QtGui.QSpinBox()
        horiz_layout.addWidget(spinbox)
        spinbox.setMinimumWidth(100)
        
        return spinbox

        
    def add_fitting_mesh_click(self):
        
        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a Mesh transform')
            return
        
        if not isinstance(sel_list[0], pm.nodetypes.Transform):
            pm.warning('Please select a Mesh transform')
            return
        '''
        try:
            mesh_shape = sel_list[0].getShape()

            if isinstance(mesh_shape, pm.nodetypes.Mesh):
                mesh_name = sel_list[0].longName() 
                
            else:
                pm.warning('Please select a Mesh transform')
                return
            
            
        except pm.general.MayaNodeError as e:
            pm.warning('Please select a Mesh transform', e)
            return
        '''
            
        #self.fitting_mesh_line_edit.setText(mesh_name)
        self.fitting_mesh_line_edit.setText(sel_list[0].longName())
        
   
    
    def add_path_click(self):
        
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Radius'])
        
        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a NurbsCurve transform')
            return
        
        if not isinstance(sel_list[0], pm.nodetypes.Transform):
            pm.warning('Please select a NurbsCurve transform')
            return
        
        try:
            crv_shape = sel_list[0].getShape()
            
            if isinstance(crv_shape, pm.nodetypes.NurbsCurve):
                crv = sel_list[0]
                
            else:
                pm.warning('Please select a NurbsCurve transform')
                return
            
            
        except pm.general.MayaNodeError as e:
            pm.warning('Please select a NurbsCurve transform', e)
            return
  
        crv_name = crv.longName()    
        self.path_line_edit.setText(crv_name)
        
        cv_list = crv.getCVs(space='world')
        num_cvs = len(cv_list)
        num_corners = num_cvs -2
        
        if num_corners < 1:
            pm.warning('Please select a degree1 curve with more than 2 CVs')
            
        
        for row in range(num_corners):
            
            item_inner = QtGui.QStandardItem('1')

            self.model.setItem(row, 0, item_inner);
    
        
    def on_build_click(self):

        
        
        pipe_radius = self.pipe_radius_spinbox.value()
        
        axis_divisions = self.axis_div_spinbox.value()
        length_divisions = self.length_div_spinbox.value()
        radial_divisions = self.radial_div_spinbox.value()
        
        crv_name = self.path_line_edit.text()
        fitting_mesh_name = self.fitting_mesh_line_edit.text()

        
        
        num_rows = self.model.rowCount()
        corner_radius_list = []
        for row in range(num_rows):
            
            radius_text = self.model.item(row,0).text()
            
            try:
                radius = float(radius_text)
                
            except ValueError as e:
                pm.warning('The Inner Radius of row {0} is not a valid number'.format(row+1))
                #print(e)
                return None
                
            
            corner_radius_list.append(radius)
        
        #print(corner_radius_list, axis_divisions, length_divisions, radial_divisions, fitting_mesh_name, crv_name, pipe_radius)
        
        
        crv = pm.PyNode(crv_name)
        
        cv_list = crv.getCVs(space='world')
        
        # get the matrix list
        #result_matrix_list = create_round_corner_matrix_list(cv_list, num_radius_div=radial_divisions)
        result_matrix_list = create_round_corner_matrix_list(cv_list, radius_list=corner_radius_list, radial_divisions=radial_divisions, length_divisions=length_divisions)
        
        # create the profile 
        profile_pos = create_profile_points(radius=pipe_radius, num_points=axis_divisions)
        
        # get the positions
        pos_list = transform_profile_list(result_matrix_list=result_matrix_list, profile_pos=profile_pos)
        
        # build mesh 
        mesh_mobj_list = build_mesh(pos_list)
        pm_mesh_list = [ pm.PyNode('|{0}'.format(m.name())) for m in mesh_mobj_list]
        pipe_grp = pm.group(em=True, name='pipe_grp')
        pm.parent(pm_mesh_list, pipe_grp)
        
        # add pipe fitting
        dup_mesh=None
        try:
            dup_mesh = pm.PyNode(fitting_mesh_name)
        except pm.MayaNodeError:
            pm.warning('could not find fitting mesh')
        
        fitting_list = add_pipe_fitting(result_matrix_list, mesh=dup_mesh)
        fitting_grp = pm.group(em=True, name='fitting_grp')
        pm.parent(fitting_list, fitting_grp)
        
        # create the main group
        main_pipe_grp = pm.group(em=True, name='main_pipe_grp')
        pm.parent(pipe_grp, fitting_grp, main_pipe_grp)
        
        pm.sets('initialShadingGroup', forceElement=pm_mesh_list)
        
                        



'''
def show():      
    win = Curve_spreadsheet(parent=maya_main_window())
    win.show()

try:
    win.close()
except NameError as e:
    print(e)
    
win = Curve_spreadsheet(parent=maya_main_window())
win.move(100, 210)
win.show()
'''

'''
crv = pm.curve(d=1, p=[(30, -15, 0), (0,0,0), (30, 15, 0), (30,30,0), (0,30,0)])


cv_list = crv.getCVs(space='world')
radius_list = [3,2,5]
radial_divisions = 10
length_divisions = 5
pipe_radius = 1
axial_divisions = 12

# add pipe fitting
dup_mesh=None
try:
    dup_mesh = pm.PyNode('fitting_grp')
except pm.MayaNodeError:
    pm.warning('could not find fitting mesh')
    
    
    
# get the matrix list
result_matrix_list = create_round_corner_matrix_list(cv_list, radius_list=radius_list, radial_divisions=radial_divisions, length_divisions=length_divisions)


def plot_mat_list(result_matrix_list):
        sp_list = []
        for m_list in result_matrix_list:
            for m in m_list:
                sp = pm.polySphere(r=.1)[0]
                sp.setMatrix(m)
                sp_list.append(sp)
                
        pm.select(sp_list)


#if result_matrix_list:
    #plot_mat_list(result_matrix_list)
 

# create the profile 
profile_pos = create_profile_points(radius=pipe_radius, num_points=axial_divisions)

# get the positions
pos_list = transform_profile_list(result_matrix_list=result_matrix_list, profile_pos=profile_pos)



# build mesh 
mesh_mobj_list = build_mesh(pos_list)
pm_mesh_list = [ pm.PyNode('|{0}'.format(m.name())) for m in mesh_mobj_list]
pipe_grp = pm.group(em=True, name='pipe_grp')
pm.parent(pm_mesh_list, pipe_grp)


fitting_list = add_pipe_fitting(result_matrix_list, mesh=dup_mesh)
fitting_grp = pm.group(em=True, name='fitting_grp')
pm.parent(fitting_list, fitting_grp)

# create the main group
main_pipe_grp = pm.group(em=True, name='main_pipe_grp')
pm.parent(pipe_grp, fitting_grp, main_pipe_grp)

pm.sets('initialShadingGroup', forceElement=pm_mesh_list)
'''




