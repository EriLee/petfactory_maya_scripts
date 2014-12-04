import petfactory.rigging.joint_tools as joint_tools
import petfactory.rigging.dynamic_curves.dynamic_curves as dynamic_curves
import pymel.core as pm
import pprint

reload(dynamic_curves)

pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/jnt_ref_v02.mb', f=True)


def build_joints(joint_ref_list):
    
    nested_jnt_list = []
    
    for index, joint_ref in enumerate(joint_ref_list):
        
        joint_info = joint_tools.build_joint_info(joint_ref, override_name='flower_{0}'.format(index))
        up_vec = joint_tools.vec_from_transform(joint_ref, 2)
        jnt_list = joint_tools.build_joint_hierarchy(joint_info, up_vec)
        nested_jnt_list.append(jnt_list)
        
    return nested_jnt_list
    


def setup_dynamic_joints(nested_jnt_list, name='name'):
    
    crv_list = []
    
    root_main_grp = pm.group(em=True, name='{0}_root_main_grp'.format(name))
    root_ctrl_grp = pm.group(parent=root_main_grp, em=True, name='{0}_root_ctrl_grp'.format(name))
    root_misc_grp = pm.group(parent=root_main_grp, em=True, name='{0}_root_misc_grp'.format(name))
 
    root_ctrl = pm.circle(normal=(1,0,0), radius =5, ch=False, name='{0}_root_ctrl'.format(name))[0]
    pm.parent(root_ctrl, root_ctrl_grp)
    root_ctrl_grp.setMatrix(nested_jnt_list[0][0].getMatrix())
    
    cluster_grp = pm.group(parent=root_ctrl, em=True, name='{0}_cluster_grp'.format(name))
    blendshape_grp = pm.group(parent=root_ctrl, em=True, name='{0}_blendshape_grp'.format(name))
    
    jnt_grp = pm.group(em=True, name='{0}_jnt_grp'.format(name))
    jnt_grp.setMatrix(nested_jnt_list[0][0].getMatrix())
    pm.parent(nested_jnt_list[0][0], jnt_grp)
    
    pm.parent(jnt_grp, root_ctrl)
    
    
    
    for index, jnt_list in enumerate(nested_jnt_list):
        
        # get the joint positions
        pos_list = [pm.joint(jnt, q=True, p=True, a=True) for jnt in jnt_list]
        
        # build the curve that we will make dynamic, and drive the ik spline rig 
        crv = pm.curve(ep=pos_list, name='original_curve')
        
        blendshape_crv = pm.duplicate(crv, name='blendshape_{0}_crv'.format(index))[0]
        pm.blendShape(blendshape_crv, crv)
        #pm.parent(blendshape_crv, blendshape_grp)
        
        num_cvs = blendshape_crv.getShape().numCVs()
        
        
        
        # loop through the cv and add cluster. On cv 0-1 add one cluster,
        # the rest of the cv will have one cluster each, 
        # might add one to the second to last and last
        for i in range(num_cvs):
            if i is 0:
                cv = '0:1'
            elif i is 1:
                continue
            else:
                cv = i
                
            clust, clust_handle = pm.cluster('{0}.cv[{1}]'.format(blendshape_crv.longName(), cv), relative=True)
            pm.parent(clust_handle, cluster_grp)
        
        crv_list.append(crv)
  
    # make the curves dynamic    
    info_dict_list = dynamic_curves.make_curves_dynamic(crv_list)
     
    # might want to delete stuff later...
    for index, info_dict in enumerate(info_dict_list):
        
        #pprint.pprint(info_dict)
        dynamic_curve = info_dict.get('curve')
        dynamic_curve.rename('dynamic_curve')  
        pm.ikHandle(solver='ikSplineSolver', curve=dynamic_curve, parentCurve=False, createCurve=False, rootOnCurve=False, twistType='easeInOut', sj=nested_jnt_list[index][0], ee=nested_jnt_list[index][-1])    
    

    # get a reference to the hairsystem and nucleus
    hairsystem = info_dict_list[0].get('hairsystem').getShape()
    nucleus = info_dict_list[0].get('nucleus')
    follicle = info_dict_list[0].get('follicle')


    pm.parent(follicle.getParent(), root_ctrl)

    
    # hairsystem
    hairsystem.startCurveAttract.set(0.005)
    #pm.select(hairsystem)
    
    
    # nucleus
    #nucleus.spaceScale.set(.1)
    nucleus.timeScale.set(10)
    #print(nucleus)
    
    
    
    
#pm.select(['group1', 'group2', 'group3', 'group4'])
pm.select(['group1'])
sel_list = pm.ls(sl=True)

nested_jnt_list = build_joints(sel_list)

setup_dynamic_joints(nested_jnt_list, name='flower')
    


#pm.select('.cv[0:1]')
#pm.select('.cv[2]')

#pm.cluster('{}.cv[{1}]'.format(crv, cv), relative=True)
#pm.cluster('{0}.cv[{1}]'.format('blendshape_0_crv', 2), relative=True)