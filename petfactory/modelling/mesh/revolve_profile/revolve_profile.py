import pymel.core as pm
import math
import pprint
import petfactory.modelling.mesh.extrude_profile as extrude_profile

# note that the order in which the objects are selected 
# affects the direction of the normals

pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/empty_scene.mb', f=True)

def sweep_proflie_pos_list(pos_list, axis_divisions):
     
    theta_inc = (math.pi*2) / (axis_divisions)
    
    # create a list of positions with a radius of one around origo
    # this vecots will later be multiplied by the pos_list to transform
    # create a sweep of the profile pos
    radial_pos_list = []
    
    for index in range(axis_divisions):
        
        u = math.cos(index*theta_inc)
        v = math.sin(index*theta_inc)
        radial_pos_list.append((u, v))

    # multiply the "unit circle sweep" with each position, adding them to the return array
    revolve_pos_list = []
    for pos in pos_list:
        
        temp_list = []
        for radial_pos in radial_pos_list:
            
            temp_list.append((pos[0], pos[1]*radial_pos[1], pos[1]*radial_pos[0]))
            
        revolve_pos_list.append(temp_list)
        
    return revolve_pos_list



def prettify_mesh(mesh):
    
    # assign default shader 
    pm.sets('initialShadingGroup', forceElement=mesh)
    # set the normal edga angle
    pm.polySoftEdge(mesh, angle=15, ch=False)
    
    pm.select(deselect=True)
    
    
pos_list = [(5,3,0), (5,5,0), (0,5,0)]
axis_divisions = 12

# create the revolved position list
revolve_pos_list = sweep_proflie_pos_list(pos_list=pos_list, axis_divisions=axis_divisions)

#pprint.pprint(len(revolve_pos_list))

len_pos_list = len(revolve_pos_list)
for index, pos_list in enumerate(revolve_pos_list):
    
    if index is 0 or index is len_pos_list-1:
        continue

    else:    
        print(index)
        
        
# build mesh from pos list       
#mesh_dependnode = extrude_profile.mesh_from_pos_list(pos_list=revolve_pos_list, name='test')         

#mesh = pm.PyNode(mesh_dependnode.name()) 
#prettify_mesh(mesh)

