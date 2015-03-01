import pymel.core as pm
import petfactory.util.vector as pet_vector


def create_joints_on_curve(crv, num_joints, up_axis, parent_joints=True, show_lra=True):
    
    crv_shape = crv.getShape()
    length = crv_shape.length()
    length_inc = length / (num_joints-1)
    
    crv_matrix = crv.getMatrix(worldSpace=True)
        
    up_vec = pm.datatypes.Vector(crv_matrix[up_axis][0], crv_matrix[up_axis][1], crv_matrix[up_axis][2])
    up_vec.normalize()
    
    
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
            
            if aim_vec.isParallel(up_vec, tol=0.1):
                pm.warning('up_vec is to close to the aim vec')
            
            # build a transform matrix from aim and up
            tm = pet_vector.remap_aim_up(aim_vec, up_vec, aim_axis=0, up_axis=2, invert_aim=False, invert_up=False, pos=prev_jnt)
            
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
    pm.select(deselect=True)
    

def cable_base_ik(crv):
    
    jnt_list = create_joints_on_curve(crv=crv, num_joints=3, up_axis=2, parent_joints=True, show_lra=True)
    
    # calculate the cv pos of the lin crv
    #crv_blendshape = 
    pm.ikHandle(sj=jnt_list[0], ee=jnt_list[-1])
    
   
    
    
#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/cable_crv.mb', f=True)

crv = pm.PyNode('curve1')

cable_base_ik(crv)
