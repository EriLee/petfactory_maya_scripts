import maya.cmds as cmds
import random
import math

def build_tiled_mesh_uv(mesh, num, t_offset, rot_scale, item_per_row_uv, item_per_row_xform):
    
    #get the x and z spacing [ xmin ymin zmin xmax ymax zmax ] 
    bb = cmds.xform(mesh, q=True, bb=True)
    x_dist = bb[3] - bb[0]
    z_dist = bb[5] - bb[2]
    
    # duplicate mesh and scale the uvs
    uv_scale = 1.0/item_per_row_uv
    temp_mesh = cmds.duplicate(mesh)[0]
    cmds.select(temp_mesh)
    cmds.select(cmds.polyListComponentConversion(tuv = True))
    cmds.polyEditUV(relative=True, scaleU=uv_scale, scaleV=uv_scale)
    
    grp = cmds.group(em=True, name='dup_group')
    
    for i in xrange(num):

        dup = cmds.duplicate(temp_mesh)
        
        # uv
        cmds.select(dup)
        cmds.select(cmds.polyListComponentConversion(tuv = True))
        cmds.polyEditUV(relative=True, uValue=(i % item_per_row_uv)*uv_scale, vValue=(math.floor(i / item_per_row_uv))*uv_scale)
        
        # translate
        cmds.xform(dup, t=[(i % item_per_row_xform)*(x_dist+t_offset[0]), 0, (math.floor(i / item_per_row_xform))*(z_dist+t_offset[2])])
        
        # rotate
        cmds.xform(dup, ro=[random.randint(-rot_scale[0],rot_scale[0]), random.randint(-rot_scale[1],rot_scale[1]), random.randint(-rot_scale[2],rot_scale[2])])
        
        cmds.parent(dup, grp)
    
    cmds.delete(temp_mesh)
    cmds.select(deselect=True)
    
    return grp
    
    
#obj = cmds.ls(sl=True)[0]

g = build_tiled_mesh_uv(    obj, 
                            num = 200,
                            t_offset = [.2, 0, .2],
                            rot_scale = [2,0, 2],
                            item_per_row_uv=10,
                            item_per_row_xform=10   )
cmds.select(g)


    