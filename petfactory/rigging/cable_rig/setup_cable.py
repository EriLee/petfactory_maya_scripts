import pymel.core as pm
import maya.cmds as cmds
import pprint

def add_curve_joints(path, num_joints=10, front_axis=2, up_axis=1):
    
    ''' creates joints that are animated along the specified curve'''

    if front_axis < 0 or front_axis > 2 or up_axis < 0 or up_axis > 2:
        pm.warning('the front or the up axis must be in range 0-2')
        return
        
    if front_axis == up_axis:
        pm.warning('the front axis can not be the same as the up axis')
        return
        
    u_front_axis = ['x', 'y', 'z'][front_axis]
    u_up_axis = ['x', 'y', 'z'][up_axis]
    
    
    ret_dict = {}
    
    joint_list = []
    motionpath_list = []
    
    ret_dict['joint_list'] = joint_list
    ret_dict['motionpath_list'] = motionpath_list

    min_u, max_u = path.getShape().getKnotDomain()
    #u_inc = max_u/(num_joints-1)
    u_inc = 1.0/(num_joints-1)

    for index in range(num_joints):
    
        # create the joints
        jnt = pm.createNode('joint', name='mp_joint_{0}'.format(index), ss=True)
        joint_list.append(jnt)
        
        # create the motion path node, if fractionMode is True it will use 0-1 u range
        motionpath = pm.pathAnimation(jnt, follow=True, bank=True, fractionMode=True, followAxis=u_front_axis, upAxis=u_up_axis, c=path)
        motionpath_list.append(motionpath)
        
        # break the uvalue anim connection
        anim_crv = pm.listConnections('{0}.uValue'.format(motionpath))
        pm.delete(anim_crv)
        
        # hook up the value that will drive the motion path
        pm.setAttr('{0}.uValue'.format(motionpath), u_inc*index)
  
    
    jnt_grp = pm.group(em=True, name='jnt_grp') 
    pm.parent(joint_list, jnt_grp)
        
    return ret_dict
        

crv = pm.PyNode('curve1')

add_curve_joints(path=crv)