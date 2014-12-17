import pymel.core as pm
import math
import petfactory.modelling.mesh.extrude_profile as extrude_profile

def draw_crv_from_pos_list(pos_list):
    
    crv = None
    for pos in pos_list:
        
        if crv is None:
            crv = pm.curve(d=1, p=[(pos[0], pos[1], 0)])
            print(crv)
            
        else:
            pass
            #pm.curve.(crv, append=True, p=[(pos[0], pos[1], 0)])
            pm.curve(crv, a=True, p=[(pos[0], pos[1], 0)] )




def sharpen_profile_corners(pos_list, sharpen_size):

    num_pos = len(pos_list)
    sharpen_pos_list = []
    
    for index, pos in enumerate(pos_list):
        
        if index is not 0 and index is not num_pos-1:
            
            sharpen_back_pos = pos + (pos_list[index-1] - pos_list[index]).normal() * sharpen_size
            sharpen_forw_pos = pos + (pos_list[index+1] - pos_list[index]).normal() * sharpen_size
            
            sharpen_pos_list.extend([sharpen_back_pos, pos, sharpen_forw_pos])
            
        
        else:
            sharpen_pos_list.append(pos)
            
    return sharpen_pos_list
    



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
    
    

   
    
        
pos_list = [pm.datatypes.Vector(p[0], p[1], 0) for p in [(0,1), (.2,1), (.2, 1.3), (.5, 1.3), (.5, 1)]]
pos_list.reverse()

sharpen_size = .02
sharpen_pos_list = sharpen_profile_corners(pos_list, sharpen_size)

    
#draw_crv_from_pos_list(pos_list=sharpen_pos_list)


revolve_pos_list = sweep_proflie_pos_list(pos_list=sharpen_pos_list, axis_divisions=12)



# create a simple pipe profilepos list

pipe_pos_list = [pm.datatypes.Vector(-4, 1, 0), pm.datatypes.Vector(-3, 1, 0), pm.datatypes.Vector(-2, 1, 0), pm.datatypes.Vector(-1, 1, 0)]
pipe_pos_list.reverse()
pipe_sweep_list = sweep_proflie_pos_list(pos_list=pipe_pos_list, axis_divisions=12)

combined_pos_list = revolve_pos_list[:]
combined_pos_list += pipe_sweep_list[:]

#combined_pos_list.extend((revolve_pos_list, pipe_sweep_list))

# build mesh from pos list       
#mesh_dependnode = extrude_profile.mesh_from_pos_list(pos_list=revolve_pos_list, name='test')
mesh_dependnode = extrude_profile.mesh_from_pos_list(pos_list=combined_pos_list, name='test')

mesh = pm.PyNode(mesh_dependnode.name()) 
prettify_mesh(mesh)




