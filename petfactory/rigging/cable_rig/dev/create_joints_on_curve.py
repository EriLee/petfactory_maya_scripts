import pymel.core as pm
import maya.api.OpenMaya as om

pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)
num_joints = 10

crv = pm.curve(d=3, p=[(-10, -10, -10), (-5, -10, -10), (0,10,0), (0, 10, 15), (10, 10, 10)])
crv_shape = crv.getShape()

pm.toggle(crv, hull=True)

#min_u, max_u = crv_shape.getKnotDomain()
#u_inc = max_u/(num_joints-1)

length = crv_shape.length()
length_inc = length / (num_joints-1)

jnt_list = []
for index in range(num_joints):
    
    u = crv_shape.findParamFromLength(length_inc*index)
    p = crv_shape.getPointAtParam(u)
    jnt = pm.createNode('joint', name='joint_{0}'.format(index), ss=True)
    pm.toggle(jnt, localAxis=True)
    jnt.translate.set(p)
    jnt_list.append(jnt)
    
    if index > 0:
        
        prev_jnt = jnt_list[index-1].getTranslation(space='world')
        curr_jnt = jnt_list[index].getTranslation(space='world')
        
        aim_vec = (curr_jnt - prev_jnt).normal()                
        up_vec = pm.datatypes.Vector(0,1,0).normal()
        cross_vec = aim_vec.cross(up_vec)
        up_vec_ortho = cross_vec.cross(aim_vec)
        tm = pm.datatypes.TransformationMatrix(    [aim_vec[0], aim_vec[1], aim_vec[2], 0], 
                                                   [up_vec_ortho[0], up_vec_ortho[1], up_vec_ortho[2], 0],
                                                   [cross_vec[0], cross_vec[1], cross_vec[2], 0],
                                                   [prev_jnt[0], prev_jnt[1], prev_jnt[2], 1])

        
        #om_tm = om.MTransformationMatrix(om.MMatrix(tm))
        #r = om_tm.rotation()
        #r_deg = pm.util.degrees((r.x, r.y, r.z))
        #print(r_deg)
        pm_rot = tm.getRotation()
        r_deg = pm.util.degrees((pm_rot[0], pm_rot[1], pm_rot[2]))
                                
        if index is num_joints-1:
            jnt_list[index-1].jointOrient.set(r_deg)
            jnt_list[index].jointOrient.set(r_deg)

        else:
            jnt_list[index-1].jointOrient.set(r_deg)
            
for index, jnt in enumerate(jnt_list):
    if index > 0:
        pm.parent(jnt_list[index], jnt_list[index-1])