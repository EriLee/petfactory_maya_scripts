import pymel.core as pm
import pprint
import math


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


def plot_profile(p_list):
    '''Plot the positions in the list'''
    
    for p in p_list:
        
        loc = pm.spaceLocator()
        loc.translate.set(p)
        loc.localScale.set((.1, .1, .1))
        

def build_proflie_rot_matrix(theta, u, v):
    '''Returns a transformation matrix that are rotated theta radians 
    around the z axis, and translated u and v in the x and y'''
    
    tm = pm.datatypes.TransformationMatrix()
    tm.addRotation(rot=(0,0,theta), order='XYZ', space='world')
    tm.addTranslation((u, v, 0), space='world')
    
    return tm
    
   
def rotate_profile_list(p_list, rot_matrix):
    
    pos = rot_matrix.getTranslation(space='world')
    ret_matrix_list = []
    
    for p in p_list:
        
        rot_p = p.rotateBy(rot_matrix) + pos
        loc = pm.spaceLocator()
        loc.translate.set(rot_p)
        loc.localScale.set((.1, .1, .1))
        ret_matrix_list.append(rot_p)
        
    return ret_matrix_list
    
    
   
#p_list = get_profile_points(radius=2, num_points=12, axis=0)
#theta = math.pi/4
#profile_rot_matrix = build_proflie_rot_matrix(theta, 4, 4)

pm.system.openFile('/Users/johan/Documents/projects/bot_pustervik/scenes/empty_scene.mb', f=True)

uv_list = [(1,3), (1.4, 1.4), (3,1)]
theta_list = [0, math.pi/4, math.pi/2]

p_list = create_profile_points(radius=1, num_points=12)
cube = pm.PyNode('pCube1')

for i in range(3):
    
    profile_rot_matrix = build_proflie_rot_matrix(theta_list[i], uv_list[i][0], uv_list[i][1])
    local_pos_list = rotate_profile_list(p_list, profile_rot_matrix)
    
    cube_matrix = pm.datatypes.TransformationMatrix(cube.getMatrix())
    pos = pm.datatypes.Vector(cube_matrix[3][0], cube_matrix[3][1], cube_matrix[3][2])
    
    for p in local_pos_list:
        print(p)
        rot_p = p.rotateBy(cube_matrix) + pos
        loc = pm.spaceLocator()
        loc.translate.set(rot_p)
        loc.localScale.set((.1, .1, .1))
    

