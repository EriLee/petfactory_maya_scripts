import pymel.core as pm
import math

pm.openFile('/Users/johan/Documents/Projects/python_dev/scenes/uv_cube.mb', f=True)

grp_list = [pm.PyNode('group{0}'.format(n)) for n in range(15)]

num_grp = len(grp_list)
items_per_row = 3
uv_scale = 1.0/items_per_row
#print(uv_scale)

for index, grp in enumerate(grp_list):
    
    shift_u = (index / (items_per_row*items_per_row))
    u_pos = ((index % items_per_row) * uv_scale) + shift_u
    v_pos = ((index / items_per_row) % items_per_row) * uv_scale 
        
    grp_uvs = pm.polyListComponentConversion(grp, tuv=True)
    
    # get the uv min ,max
    (u_min, u_max), (v_min, v_max) = pm.polyEvaluate(grp_uvs, boundingBox2d=True)
    
    #pm.polyEditUV(grp_uvs, v=1, relative=True)
    pm.polyEditUV(grp_uvs, scale=True, scaleU=uv_scale, scaleV=uv_scale)#, pivotU=u_min, pivotV=v_min)
    pm.polyEditUV(grp_uvs, u=u_pos, v=v_pos)


pm.select(grp_list)