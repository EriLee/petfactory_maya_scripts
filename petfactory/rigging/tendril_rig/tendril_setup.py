import pymel.core as pm
import maya.cmds as cmds
import pprint
import petfactory.rigging.joint_tools as joint_tools
import petfactory.rigging.nhair.nhair_dynamics as nhair_dynamics
reload(nhair_dynamics)

pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/jnt_ref_v02.mb', f=True)


# build the joints from the joint ref group
def build_joints(joint_ref_list, name_list=None):
    
    ret_list = []
       
    for index, joint_ref in enumerate(joint_ref_list):
        
        if name_list is not None:
            
            if len(joint_ref_list) != len(name_list):
                pm.warning('The length of name list does not match the ref list! ref name used instead')
                name = joint_ref.nodeName()
                
            else:
                name = name_list[index]
        else:
            name = joint_ref.nodeName()
        
        #joint_info = joint_tools.build_joint_info(joint_ref, override_name='{0}_{1}'.format(name, index))
        joint_info = joint_tools.build_joint_info(joint_ref, override_name='{0}'.format(name))
        up_vec = joint_tools.vec_from_transform(joint_ref, 2)
        jnt_list = joint_tools.build_joint_hierarchy(joint_info, up_vec)
        
        ret_list.append({name:jnt_list})  
        
    return ret_list
    



def setup_dynamic_joint_chain(jnt_dict, existing_hairsystem=None):
    
    #pprint.pprint(jnt_dict)
    
    ret_dict = {}
    
    name = jnt_dict.keys()[0]
    jnt_list = jnt_dict.get(name)
    
    # create groups
    root_main_grp = pm.group(em=True, name='{0}_root_main_grp'.format(name))
    root_ctrl_grp = pm.group(parent=root_main_grp, em=True, name='{0}_root_ctrl_grp'.format(name))
    root_misc_grp = pm.group(parent=root_main_grp, em=True, name='{0}_root_misc_grp'.format(name))
    root_hidden_grp = pm.group(parent=root_misc_grp, em=True, name='{0}_root_hidden_grp'.format(name))
    
    
    # ctrl
    root_ctrl = pm.circle(normal=(1,0,0), radius=5, ch=False, name='{0}_root_ctrl'.format(name))[0]
    pm.parent(root_ctrl, root_ctrl_grp)
    root_ctrl_grp.setMatrix(jnt_list[0].getMatrix())
    
    # add attr to ctrl
    pm.addAttr(root_ctrl, longName='blendshape', minValue=0.0, maxValue=1.0, defaultValue=1.0, keyable=True)
    pm.addAttr(root_ctrl, longName='stretchScale', minValue=0.0, defaultValue=1.0, keyable=True)


    
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
    blendshape = pm.blendShape(blendshape_crv, crv, origin='world')[0]

    root_ctrl.blendshape >> blendshape.weight[0]
    
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
            
        clust, clust_handle = pm.cluster('{0}.cv[{1}]'.format(blendshape_crv.longName(), cv), relative=True, name='{0}_{1}_cluster_'.format(name, i))
        pm.parent(clust_handle, cluster_grp)
        
        
    # if we parent and and set zero out the transforms, the cluster and blendshape curves plays along :)
    # with no offset... hmmm need to check out why this is...
    pm.parent(blendshape_crv, blendshape_grp)
    blendshape_crv.translate.set(0,0,0)
    blendshape_crv.rotate.set(0,0,0)
    
    
    
    # make the curves dynamic    
    nhair_dict_list = nhair_dynamics.make_curve_dynamic(crv)
    
    #pprint.pprint(info_dict_list)
    
    output_curve = nhair_dict_list.get('output_curve')
    follicle = nhair_dict_list.get('follicle')
    nucleus = nhair_dict_list.get('nucleus')
    hairsystem = nhair_dict_list.get('hairsystem')
    
    
    # output curve
    if output_curve:
        iks_handle, effector = pm.ikHandle(solver='ikSplineSolver', curve=output_curve, parentCurve=False, createCurve=False, rootOnCurve=False, twistType='easeInOut', sj=jnt_list[0], ee=jnt_list[-1])
        pm.parent(iks_handle, root_hidden_grp)
        ret_dict['output_curve'] = output_curve
        output_curve_shape = output_curve.getShape()
        
        output_curve_info = pm.arclen(output_curve, ch=True)
    
    else:
        print('could not access the output curve')  
          
      
    # follicle    
    if follicle:
        pm.setAttr('{}.pointLock'.format(follicle.getShape()), 1)
        pm.parent(follicle.getParent(), root_ctrl)
        ret_dict['follicle'] = follicle
        
    else:
        print('could not access the follicle')
      
      
    # nucleus    
    if nucleus:
        nucleus.timeScale.set(10)
        ret_dict['nucleus'] = nucleus
        
    else:
        print('could not access the nucleus')
        
        
    
    # hair system  
    if hairsystem:
        
        # if we want to use an existing hair system
        if existing_hairsystem is not None:
            print('Delete current hairsystem, use {0}'.format(existing_hairsystem))
            
            num_connection = len(pm.listConnections('{0}.inputHair'.format(hairsystem_1)))
            
            follicle.outHair >> existing_hairsystem.inputHair[num_connection]
            existing_hairsystem.outputHair[num_connection] >> follicle.currentPosition
            
            pm.delete(hairsystem)
            
        else:         
            hairsystem.startCurveAttract.set(0.005)
            
        ret_dict['hairsystem'] = hairsystem
        
        
    else:
        print('could not access the hairsystem')
        
    
    # make curves unselectable
    crv.overrideEnabled.set(1)
    crv.overrideDisplayType.set(2)
    
    blendshape_crv.overrideEnabled.set(1)
    blendshape_crv.overrideDisplayType.set(2)
    
    output_curve_shape.overrideEnabled.set(1)
    output_curve_shape.overrideDisplayType.set(2)
    
    # hide the hidden group
    root_hidden_grp.visibility.set(0)
    
    # make the joint group unselectable
    jnt_grp.overrideEnabled.set(1)
    jnt_grp.overrideDisplayType.set(2)
    
    
    
    # setup the joint stretch
    arc_length = output_curve_info.arcLength.get()
    
    md_global_scale = pm.createNode('multiplyDivide', name='global_scale_compensate')
    md_global_scale.operation.set(2)
    
    output_curve_info.arcLength >> md_global_scale.input1X
    root_ctrl.sx >> md_global_scale.input2X
    
    stretch_scale_mult = pm.createNode('multDoubleLinear', name='stretch_scale_mult')
    md_global_scale.outputX >> stretch_scale_mult.input1
    root_ctrl.stretchScale >> stretch_scale_mult.input2

    
    for index, jnt in enumerate(jnt_list):
        
        if index is not 0:
            mult_double = pm.createNode('multDoubleLinear', name='jnt_{0}_stretch_mult'.format(index))
            mult_double.input1.set(jnt.tx.get() / arc_length)
            #output_curve_info.arcLength >> mult_double.input2
            #md_global_scale.outputX >> mult_double.input2
            stretch_scale_mult.output >> mult_double.input2
            mult_double.output >> jnt.tx
            
    
    return ret_dict
        
        

    
#pm.select(['group1', 'group2', 'group3', 'group4'])
#pm.select(['group1', 'group2', 'group3'])
pm.select(['group1'])
sel_list = pm.ls(sl=True)
jnt_dict_list = build_joints(sel_list)
dyn_joint_dict_1 = setup_dynamic_joint_chain(jnt_dict_list[0])


'''
node = pm.PyNode('flower_jnt_pos')
ref_list = [node, node, node, node]

# build the joints
jnt_dict_list = build_joints(ref_list, name_list=['tendri_1', 'tendril_2', 'tendril_3', 'tendril_4'])

# set up the nhair dynamics
output_curve_list = []
output_curve_grp = pm.group(em=True, name='output_curve_grp')

dyn_joint_dict_1 = setup_dynamic_joint_chain(jnt_dict_list[0])
hairsystem_1 = dyn_joint_dict_1.get('hairsystem')
output_curve_list.append(dyn_joint_dict_1.get('output_curve'))


dyn_joint_dict_2 = setup_dynamic_joint_chain(jnt_dict_list[1], existing_hairsystem=hairsystem_1)
output_curve_list.append(dyn_joint_dict_2.get('output_curve'))


dyn_joint_dict_3 = setup_dynamic_joint_chain(jnt_dict_list[2], existing_hairsystem=hairsystem_1)
output_curve_list.append(dyn_joint_dict_3.get('output_curve'))

dyn_joint_dict_4 = setup_dynamic_joint_chain(jnt_dict_list[3], existing_hairsystem=hairsystem_1)
output_curve_list.append(dyn_joint_dict_4.get('output_curve'))

for output_curve in output_curve_list:
    curve_parent = output_curve.getParent()
    pm.parent(output_curve, output_curve_grp)
    pm.delete(curve_parent)
    
'''


