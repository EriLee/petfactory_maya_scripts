import pymel.core as pm
import math
import pprint
import petfactory.modelling.mesh.extrude_profile as extrude_profile

# note that the order in which the objects are selected 
# affects the direction of the normals


pos_list = [ pm.PyNode(s.longName()).translate.get() for s in pm.ls(sl=True)]

axis_divisions = 36
theta_inc = (math.pi*2) / (axis_divisions)

radial_pos_list = []
for index in range(axis_divisions):
    
    u = math.cos(index*theta_inc)
    v = math.sin(index*theta_inc)
    radial_pos_list.append((u, v))

    
revolve_pos_list = []
for pos in pos_list:
    
    temp_list = []
    for radial_pos in radial_pos_list:
        
        temp_list.append((pos[0], pos[1]*radial_pos[1], pos[1]*radial_pos[0]))
        
    revolve_pos_list.append(temp_list)

#revolve_pos_list.reverse()
        
mesh_dependnode = extrude_profile.mesh_from_pos_list(pos_list=revolve_pos_list, name='test')         
pm_mesh = pm.PyNode(mesh_dependnode.name())  
pm.sets('initialShadingGroup', forceElement=pm_mesh)