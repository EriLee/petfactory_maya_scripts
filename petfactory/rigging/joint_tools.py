
import pymel.core as pm

try:
    import petfactory.util.vector as util_vec
    
except ImportError as e:
    print('The script requires module "petfactory.util.vector"\n{0}'.format(e))


def build_joint_hierarchy(info_list, up_vector, aim_axis=0, up_axis=2, invert_aim=False, invert_up=False, prefix='prefix', suffix='suffix'):
    '''
    build a joint hierarchy. info_list is a list of dicts that contains the name of the joint and the position
    
    info_list = [   {'name':'one', 'pos':(0,0,0)},
                    {'name':'two', 'pos':(0,10,10)}
                ]

    this dict can be created using the utility function "build_joint_info" that takes a group as a param
    and will use the child transforms to construct the info_list.

    the up_vector is the axis that will be used to rotate (bend) the joint.
    the aim_vector is the axis that will point "down/up" the joint, i.e. the twist axis.

    invert_aim
    invert_up
    prefix
    suffix

    '''

    if aim_axis == up_axis:
        pm.warning('The joint aim axis can not be equal to the joint up axis!')
        return
        
    # create a pymel vector and normalize
    up_vec = pm.datatypes.Vector(up_vector[0], up_vector[1], up_vector[2])
          
    jnt_list = []
    
    for index, info in enumerate(info_list):
        
        name = info.get('name')
                       
        start_pos = info.get('pos')        
        start_vec = pm.datatypes.Vector(start_pos[0], start_pos[1], start_pos[2])
        
        # if we are at the last joint
        if index is len(info_list)-1:
            end_pos = info_list[index-1].get('pos')
            end_vec = pm.datatypes.Vector(end_pos[0], end_pos[1], end_pos[2])
            aim_vec = start_vec - end_vec
            
        else:
            end_pos = info_list[index+1].get('pos')
            end_vec = pm.datatypes.Vector(end_pos[0], end_pos[1], end_pos[2])
            aim_vec = end_vec - start_vec
                   
        tm = util_vec.remap_aim_up(aim_vec=aim_vec, up_vec=up_vec, aim_axis=aim_axis, up_axis=up_axis, pos=start_vec, invert_aim=invert_aim, invert_up=invert_up)        
        
        # get the euler angles form the matrix and convert from rad ro deg
        rot_rad = tm.getRotation()
        rot_deg = pm.datatypes.degrees(rot_rad)
          
        # create the joint
        jnt = pm.createNode('joint', ss=True, name='{0}_{1}_jnt_{2}'.format(prefix, name, suffix))

        # set the joint orients and translation
        pm.setAttr('{0}.jointOrientX'.format(jnt), rot_deg[0])
        pm.setAttr('{0}.jointOrientY'.format(jnt), rot_deg[1])
        pm.setAttr('{0}.jointOrientZ'.format(jnt), rot_deg[2])
    
        jnt.translate.set(start_vec)
        
        jnt_list.append(jnt)
        
    
    # parent the joints
    index = len(jnt_list)-1
    while index > 0:
        index -= 1
        pm.parent(jnt_list[index+1], jnt_list[index])
     
    pm.select(deselect=True)
    

    return jnt_list
    

def build_joint_info(group_name):
    '''Build the info list that contains dicts with the name and pos'''
    info_list = []
    
    jnt_grp = pm.PyNode(group_name)
    node_list = pm.listRelatives(jnt_grp, children=True)
    
    for node in node_list:
        
        info_list.append({'name':node.nodeName(), 'pos':pm.xform(node, q=True, ws=True, translation=True)})

    return info_list

def vec_from_transform(group_name, axis):
    
    jnt_grp = pm.PyNode(group_name)
    
    # get the vector to be used as the "up vector" for the joint rotation, the axis that the 
    # joint rotates around, i.e. "bend" we use z-axis, the twist of the joints is using the x-axis
    m = jnt_grp.getMatrix(worldSpace=True)
    vx = pm.datatypes.Vector(m[0][0], m[0][1], m[0][2])
    vy = pm.datatypes.Vector(m[1][0], m[1][1], m[1][2])
    vz = pm.datatypes.Vector(m[2][0], m[2][1], m[2][2])
    
    axis_list = [vx, vy, vz]
    
    # Return a normalized vec
    return  axis_list[axis].normal()
    
'''

pm.openFile('/Users/johan/Dev/maya/build_joint_hierarchy/jnt_ref_v02.mb', force=True)


info_list = [ {'name':'one', 'pos':(0,0,0)},
               {'name':'two', 'pos':(0,10,10)},
               {'name':'three', 'pos':(0,20,10)}
             ]


up_vec = (1,0,0)



up_vec = vec_from_transform('jnt_grp', 0)
info_list = build_joint_info('jnt_grp')




jnt_list = build_joint_hierarchy(info_list=info_list, up_vector=up_vec, aim_axis=1, up_axis=2, invert_aim=False, invert_up=False)
pm.toggle(jnt_list, localAxis=True)

'''