import pymel.core as pm
import pprint
import math


def get_profile_points(radius, num_points):
    
    ang_inc = (math.pi*2)/num_points
    
    p_list = []
    
    for i in range(num_points):
        u = math.cos(ang_inc*i)*radius
        v = math.sin(ang_inc*i)*radius
        p_list.append(pm.datatypes.Vector(u, 0, v))
     
    return p_list

def plot_profile(p_list):
     
    for p in p_list:
        
        loc = pm.spaceLocator()
        loc.translate.set(p)
        loc.localScale.set((.1, .1, .1))
        

pm.system.openFile('/Users/johan/Documents/projects/bot_pustervik/scenes/empty_scene.mb', f=True)

#plot_profile()


def build_proflie_rot_matrix(theta, u, v):
        
    tm = pm.datatypes.TransformationMatrix()
    tm.addRotation(rot=(0,0,theta), order='XYZ', space='world')
    tm.addTranslation((u, v, 0), space='world')
    
    return tm
    
   
def rotate_profile_list(p_list, rot_matrix):
    
    pos = rot_matrix.getTranslation(space='world')
    
    for p in p_list:
        
        rot_p = p.rotateBy(rot_matrix) + pos
        loc = pm.spaceLocator()
        loc.translate.set(rot_p)
        loc.localScale.set((.1, .1, .1))
    
   
#p_list = get_profile_points(radius=2, num_points=12, axis=0)
#theta = math.pi/4
#profile_rot_matrix = build_proflie_rot_matrix(theta, 4, 4)


uv_list = [(1,3), (1.4, 1.4), (3,1)]
theta_list = [0, math.pi/4, math.pi/2]

p_list = get_profile_points(radius=1, num_points=12)


for i in range(3):
    
    profile_rot_matrix = build_proflie_rot_matrix(theta_list[i], uv_list[i][0], uv_list[i][1])
    rotate_profile_list(p_list, profile_rot_matrix)

