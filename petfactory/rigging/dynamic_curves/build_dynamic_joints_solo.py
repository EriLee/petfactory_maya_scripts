import pymel.core as pm
import maya.cmds as cmds
import pprint
import petfactory.rigging.joint_tools as joint_tools
import petfactory.rigging.dynamic_curves.nhair_dynamics as nhair_dynamics
reload(nhair_dynamics)



pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/jnt_ref_v02.mb', f=True)


# build the joints from the joint ref group
def build_joints(joint_ref_list):
    
    ret_list = []
       
    for index, joint_ref in enumerate(joint_ref_list):
        
        name = joint_ref.nodeName()
        joint_info = joint_tools.build_joint_info(joint_ref, override_name='{0}_{1}'.format(name, index))
        up_vec = joint_tools.vec_from_transform(joint_ref, 2)
        jnt_list = joint_tools.build_joint_hierarchy(joint_info, up_vec)
        
        ret_list.append({name:jnt_list})  
        
    return ret_list
    



def setup_dynamic_joint_chain(jnt_dict):
    
    #pprint.pprint(jnt_dict)
    
    name = jnt_dict.keys()[0]
    jnt_list = jnt_dict.get(name)
    
    # create groups
    root_main_grp = pm.group(em=True, name='{0}_root_main_grp'.format(name))
    root_ctrl_grp = pm.group(parent=root_main_grp, em=True, name='{0}_root_ctrl_grp'.format(name))
    root_misc_grp = pm.group(parent=root_main_grp, em=True, name='{0}_root_misc_grp'.format(name))
    
    
    # ctrl
    root_ctrl = pm.circle(normal=(1,0,0), radius=5, ch=False, name='{0}_root_ctrl'.format(name))[0]
    pm.parent(root_ctrl, root_ctrl_grp)
    root_ctrl_grp.setMatrix(jnt_list[0].getMatrix())
    
    # cluster group
    cluster_grp = pm.group(parent=root_ctrl, em=True, name='{0}_cluster_grp'.format(name))
    blendshape_grp = pm.group(parent=root_ctrl, em=True, name='{0}_blendshape_grp'.format(name))
    
    # jnt group
    jnt_grp = pm.group(em=True, name='{0}_jnt_grp'.format(name))
    jnt_grp.setMatrix(jnt_list[0].getMatrix())
    pm.parent(jnt_list[0], jnt_grp)
    pm.parent(jnt_grp, root_ctrl)
      
    
    # get the joint positions
    pos_list = [pm.joint(jnt, q=True, p=True, a=True) for jnt in jnt_list]


    # build the curve that we will make dynamic, and drive the ik spline rig 
    crv = pm.curve(ep=pos_list, name='{0}_orig_curve'.format(name))
    
    # duplicate and create a blendshape curve
    blendshape_crv = pm.duplicate(crv, name='{0}_blendshape_crv'.format(name))[0]
    pm.blendShape(blendshape_crv, crv, origin='world')
    
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
        
        
    # if we parent and and set zero out the transforms, the cluster and blendshape curves plays along :)
    # with no offset... hmmm need to check out why this is...
    pm.parent(blendshape_crv, blendshape_grp)
    blendshape_crv.translate.set(0,0,0)
    blendshape_crv.rotate.set(0,0,0)
    
    
    
    # make the curves dynamic    
    info_dict_list = nhair_dynamics.make_curve_dynamic(crv)


 
    
#pm.select(['group1', 'group2', 'group3', 'group4'])
pm.select(['group1'])
sel_list = pm.ls(sl=True)

jnt_dict_list = build_joints(sel_list)


setup_dynamic_joint_chain(jnt_dict_list[0])