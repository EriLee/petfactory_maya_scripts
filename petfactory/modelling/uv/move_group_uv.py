import pymel.core as pm
import math


def tile_group_uv(grp_list, items_per_row, start_u=0, start_v=0):
    
    tile_list = []
    uv_scale = 1.0/items_per_row
    
    for index, grp in enumerate(grp_list):
        
        # when we have filled one tile create a new list and append to the tile_list
        if index % (items_per_row*items_per_row) is 0:
            temp_list = []
            tile_list.append(temp_list)
            
        #tile_list.append()
        shift_u = (index / (items_per_row*items_per_row))
        
        u_pos = ((index % items_per_row) * uv_scale) + shift_u  + start_u
        v_pos = (((index / items_per_row) % items_per_row) * uv_scale ) + start_v
            
        grp_uvs = pm.polyListComponentConversion(grp, tuv=True)
        temp_list.append(grp_uvs)
        
        # get the uv min ,max
        (u_min, u_max), (v_min, v_max) = pm.polyEvaluate(grp_uvs, boundingBox2d=True)
        
        #pm.polyEditUV(grp_uvs, v=1, relative=True)
        pm.polyEditUV(grp_uvs, scale=True, scaleU=uv_scale, scaleV=uv_scale)#, pivotU=u_min, pivotV=v_min)
        pm.polyEditUV(grp_uvs, u=u_pos, v=v_pos)
     
    return tile_list

pm.openFile('/Users/johan/Documents/Projects/python_dev/scenes/uv_cube.mb', f=True)

grp_list = [pm.PyNode('group{0}'.format(n)) for n in range(15)]
#pm.select(grp_list)
tile_list = tile_group_uv(grp_list=grp_list, items_per_row=2, start_u=0, start_v=0)

pm.select(tile_list[0])
