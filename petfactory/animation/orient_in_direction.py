import pymel.core as pm
import math

#sel = pm.ls(sl=True)[0]
sel = pm.PyNode('locator1')

curr_time = pm.currentTime(query=True)
frame_start = 1
frame_end = 120
#last_pos = pm.datatypes.Vector(0,0,0)
curr_pos = None
up_vec = pm.datatypes.Vector(0,1,0)


try:
    cube_grp = pm.PyNode('cube_grp')
    pm.delete(cube_grp)
    
except pm.MayaNodeError as e:
    print e

cube_grp = pm.group(em=True, name='cube_grp')



pm.currentTime(frame_start-1, update=True, edit=True)
last_pos = sel.translate.get()

for frame in range(frame_start, frame_end+1):
    
    pm.currentTime(frame, update=True, edit=True)
    
    curr_pos = sel.translate.get()
    aim_vec = curr_pos - last_pos
    aim_vec.normalize()
    
    cross_vec = aim_vec.cross(up_vec)
    cross_vec.normalize()
    
    up_vec_ortho = cross_vec.cross(aim_vec)
    

    matrix = pm.datatypes.TransformationMatrix(    [aim_vec[0], aim_vec[1], aim_vec[2], 0],
                                                    [up_vec_ortho[0],up_vec_ortho[1], up_vec_ortho[2], 0],
                                                    [cross_vec[0], cross_vec[1],cross_vec[2], 0],
                                                    [curr_pos[0],curr_pos[1],curr_pos[2],1])
    rot_rad = matrix.getRotation()
    #rot_y = 180/math.pi * rot_rad[1]
    rot_deg = 180/math.pi * rot_rad
    #print(rot_y)
    
    
    cube = pm.polyCube(name='cube_{0}'.format(frame))[0]
    #cube.setMatrix(matrix)
    cube.translate.set(curr_pos)
    cube.rotate.set(rot_deg)
    pm.parent(cube, cube_grp)
    
    last_pos = curr_pos
    
    
# reset the time slider
pm.currentTime(curr_time)