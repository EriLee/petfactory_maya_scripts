import petfactory.rigging.joint_tools as joint_tools
import petfactory.rigging.dynamic_curves.dynamic_curves as dynamic_curves
import pymel.core as pm
import pprint

reload(dynamic_curves)

pm.system.openFile('/Users/johan/Desktop/jnt_ref.mb', f=True)



def create_dynamic_joints(joint_ref_list):

    nested_jnt_list = []
    crv_list = []
    
    for joint_ref in joint_ref_list:
        
        joint_info = joint_tools.build_joint_info(joint_ref, override_name='flower')
        up_vec = joint_tools.vec_from_transform(joint_ref, 2)
        
        jnt_list = joint_tools.build_joint_hierarchy(joint_info, up_vec)
        
        nested_jnt_list.append(jnt_list)
        pos_list = []
        
        for jnt in jnt_list:
            pos_list.append(pm.joint(jnt, q=True, p=True, a=True))
            
        crv = pm.curve(ep=pos_list, name='original_curve')
        crv_list.append(crv)
        
    
    
    info_dict_list = dynamic_curves.make_curves_dynamic(crv_list)
    
    
    # might want to delete stuff later...
    
    for index, info_dict in enumerate(info_dict_list):
        
        #print(info_dict)
        dynamic_curve = info_dict.get('curve')
        dynamic_curve.rename('dynamic_curve')  
        pm.ikHandle(solver='ikSplineSolver', curve=dynamic_curve, parentCurve=False, createCurve=False, rootOnCurve=False, twistType='easeInOut', sj=nested_jnt_list[index][0], ee=nested_jnt_list[index][-1])    
    

pm.select(['group1', 'group2', 'group3'])
sel_list = pm.ls(sl=True)

create_dynamic_joints(sel_list)
    
