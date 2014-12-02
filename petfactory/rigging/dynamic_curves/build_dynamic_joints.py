import petfactory.rigging.joint_tools as joint_tools
import petfactory.rigging.dynamic_curves.dynamic_curves as dynamic_curves
import pymel.core as pm


reload(dynamic_curves)


def create_dynamic_joints(joint_ref_list):

    crv_list = []
    
    for joint_ref in joint_ref_list:
        
        joint_info = joint_tools.build_joint_info(joint_ref, override_name='flower')
        up_vec = joint_tools.vec_from_transform(joint_ref, 2)
        
        jnt_list = joint_tools.build_joint_hierarchy(joint_info, up_vec)
        
        pos_list = []
        
        for jnt in jnt_list:
            pos_list.append(pm.joint(jnt, q=True, p=True, a=True))
            
        crv = pm.curve(ep=pos_list, name='dynamic_curve')
        crv_list.append(crv)
        
    
    
    dynamic_curves.make_curves_dynamic(crv_list)
    


sel_list = pm.ls(sl=True)

create_dynamic_joints(sel_list)
    
