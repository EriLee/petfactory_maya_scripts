import pymel.core as pm
import maya.api.OpenMaya as om

pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)


def create_joints_on_curve(crv, num_joints, parent_joints=True, show_lra=True):
    
    crv_shape = crv.getShape()
    length = crv_shape.length()
    length_inc = length / (num_joints-1)
    
    jnt_list = []
    for index in range(num_joints):
        
        u = crv_shape.findParamFromLength(length_inc*index)
        p = crv_shape.getPointAtParam(u, space='world')
        jnt = pm.createNode('joint', name='joint_{0}'.format(index), ss=True)
        jnt.translate.set(p)
        jnt_list.append(jnt)
        
        if index > 0:
            
            prev_jnt = jnt_list[index-1].getTranslation(space='world')
            curr_jnt = jnt_list[index].getTranslation(space='world')
            
            aim_vec = (curr_jnt - prev_jnt).normal()             
            up_vec = pm.datatypes.Vector(0,1,0)
            
            # if the aim and up vec are effectively (within a certain tolerance) colinear, the
            # resulting perpendicualar vector will not be vaild in this case the negative z axis
            # will be used as up vector
            if aim_vec.isParallel(up_vec, tol=0.1):
                
                up_vec = pm.datatypes.Vector(0,0,-1)
                
                cross_vec = aim_vec.cross(up_vec)
                up_vec_ortho = cross_vec.cross(aim_vec)
                tm = pm.datatypes.TransformationMatrix(    [aim_vec[0], aim_vec[1], aim_vec[2], 0],
                                                           [cross_vec[0], cross_vec[1], cross_vec[2], 0],
                                                           [up_vec_ortho[0], up_vec_ortho[1], up_vec_ortho[2], 0],
                                                           [prev_jnt[0], prev_jnt[1], prev_jnt[2], 1])            
            else:
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
                
                
            if show_lra:
                pm.toggle(jnt, localAxis=True)
                
                
    parent_joint_list(jnt_list)
    
    return jnt_list
            
            
            
def parent_joint_list(joint_list):         
    for index, jnt in enumerate(joint_list):
        if index > 0:
            pm.parent(joint_list[index], joint_list[index-1])
    
    



#crv = pm.curve(d=3, p=[(0,0,0), (0,5,0), (0,10,0), (0,15,0), (0,15,5)])
#crv = pm.ls(sl=True)[0]
crv = pm.PyNode('curve1')    
pm.toggle(crv, hull=True)

# build the joints on curve
jnt_list = create_joints_on_curve(crv, num_joints=10)

# create the ctrl
start_ctrl = pm.circle(normal=(1,0,0))[0]
end_ctrl = pm.circle(normal=(1,0,0))[0]

start_ctrl.setMatrix(jnt_list[0].getMatrix(worldSpace=True))
end_ctrl.setMatrix(jnt_list[-1].getMatrix(worldSpace=True))

pm.duplicate(jnt_list[0])
iks_handle, effector = pm.ikHandle(solver='ikSplineSolver', curve=crv, parentCurve=False, createCurve=False, rootOnCurve=False, twistType='easeInOut', sj=jnt_list[0], ee=jnt_list[-1])

