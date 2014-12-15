import pymel.core as pm
import maya.cmds as cmds
import pprint
import petfactory.rigging.joint_tools as joint_tools
import petfactory.rigging.nhair.nhair_dynamics as nhair_dynamics
reload(nhair_dynamics)

#pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/jnt_ref_v02.mb', f=True)
pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/tendril_thin_mesh_v03.mb', f=True)



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
    num_jnt = len(jnt_list)
    
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
    pm.addAttr(root_ctrl, longName='origBlendshape', minValue=0.0, maxValue=1.0, defaultValue=1.0, keyable=True)
    pm.addAttr(root_ctrl, longName='IkSplineBlendshape', minValue=0.0, maxValue=1.0, defaultValue=0.0, keyable=True)
    pm.addAttr(root_ctrl, longName='stretchScale', minValue=0.0, defaultValue=1.0, keyable=True)
    
    pm.addAttr(root_ctrl, longName='sineY', keyable=True)
    pm.addAttr(root_ctrl, longName='sine_y_global_scale', keyable=True)
    
    pm.addAttr(root_ctrl, longName='sineZ', keyable=True)
    pm.addAttr(root_ctrl, longName='sine_z_global_scale', keyable=True)
    
    pm.addAttr(root_ctrl, longName='time', keyable=True)
    
    
    
    

    for index in range(num_jnt):
        pm.addAttr(root_ctrl, longName='sine_y_offset{0}'.format(index), keyable=True, defaultValue=index*10)
    
    
    for index in range(num_jnt):
        pm.addAttr(root_ctrl, longName='sine_y_scale{0}'.format(index), keyable=True, defaultValue=index)
        
    
    for index in range(num_jnt):
        pm.addAttr(root_ctrl, longName='sine_z_offset{0}'.format(index), keyable=True, defaultValue=index*10)
    
    
    for index in range(num_jnt):
        pm.addAttr(root_ctrl, longName='sine_z_scale{0}'.format(index), keyable=True, defaultValue=index)

 
    # cluster group
    cluster_grp = pm.group(parent=root_ctrl, em=True, name='{0}_cluster_grp'.format(name))
    rig_crv_grp = pm.group(parent=root_ctrl, em=True, name='{0}_rig_crv_grp'.format(name))
    
    # jnt group
    jnt_grp = pm.group(em=True, name='{0}_jnt_grp'.format(name))
    jnt_grp.setMatrix(jnt_list[0].getMatrix())
    pm.parent(jnt_list[0], jnt_grp)
    pm.parent(jnt_grp, root_ctrl)
    
    # bind jnt group
    main_bind_jnt_grp = pm.group(em=True, name='{0}_main_bind_jnt_grp'.format(name))
    main_bind_jnt_grp.setMatrix(jnt_list[0].getMatrix())
    pm.parent(main_bind_jnt_grp, root_ctrl)
    
   
    
    # get the joint positions
    pos_list = [pm.joint(jnt, q=True, p=True, a=True) for jnt in jnt_list]


    # build the curve that we will make dynamic, and drive the ik spline rig 
    crv = pm.curve(ep=pos_list, name='{0}_orig_curve'.format(name))
    
    # duplicate and create a blendshape curve
    blendshape_crv = pm.duplicate(crv, name='{0}_blendshape_crv'.format(name))[0]
    blendshape = pm.blendShape(blendshape_crv, crv, origin='world')[0]
    result_spline_crv = pm.duplicate(crv, name='{0}_result_spline_crv'.format(name))[0]

    root_ctrl.origBlendshape >> blendshape.weight[0]   
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
    pm.parent(blendshape_crv, rig_crv_grp)
    blendshape_crv.translate.set(0,0,0)
    blendshape_crv.rotate.set(0,0,0)
    
    
    
    # make the curves dynamic    
    nhair_dict_list = nhair_dynamics.make_curve_dynamic(crv)
    
    output_curve = nhair_dict_list.get('output_curve')
    follicle = nhair_dict_list.get('follicle')
    nucleus = nhair_dict_list.get('nucleus')
    hairsystem = nhair_dict_list.get('hairsystem')
    
    
    # output curve
    if output_curve:
        
        # add a crv that we can switch between the cluster driven crv and the dynamic output ctv
        pm.connectAttr('{0}.worldSpace[0]'.format(blendshape_crv), '{0}.create'.format(result_spline_crv))
        pm.parent(result_spline_crv, rig_crv_grp)
        result_spline_crv.translate.set(0,0,0)
        result_spline_crv.rotate.set(0,0,0)
        
        # blendshape between the cluster driben crv and the dynamic output crv
        result_blendshape = pm.blendShape(output_curve, result_spline_crv, origin='world')[0]
        root_ctrl.IkSplineBlendshape >> result_blendshape.weight[0]  

        # create a ik spline
        iks_handle, effector = pm.ikHandle(solver='ikSplineSolver', curve=result_spline_crv, parentCurve=False, createCurve=False, rootOnCurve=False, twistType='easeInOut', sj=jnt_list[0], ee=jnt_list[-1])
        pm.parent(iks_handle, root_hidden_grp)
        ret_dict['output_curve'] = output_curve
        output_curve_shape = output_curve.getShape()
        
        #output_curve_info = pm.arclen(output_curve, ch=True)
        result_spline_info = pm.arclen(result_spline_crv, ch=True)
        
  
    
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
        
    
    # make curves unselectable, enable drawing ovewrride and set to template
    for c in [crv, blendshape_crv, output_curve_shape, result_spline_crv, jnt_grp]:
        c.overrideEnabled.set(1)
        c.overrideDisplayType.set(2)
   
    # hide the hidden group
    root_hidden_grp.visibility.set(0)
 
    # setup the joint stretch
    arc_length = result_spline_info.arcLength.get()
    
    md_global_scale = pm.createNode('multiplyDivide', name='global_scale_compensate')
    md_global_scale.operation.set(2)
    
    result_spline_info.arcLength >> md_global_scale.input1X
    root_ctrl.sx >> md_global_scale.input2X
    
    stretch_scale_mult = pm.createNode('multDoubleLinear', name='stretch_scale_mult')
    md_global_scale.outputX >> stretch_scale_mult.input1
    root_ctrl.stretchScale >> stretch_scale_mult.input2

    
    bind_jnt_list = []
    for index, jnt in enumerate(jnt_list):
        
        if index is not 0:
            mult_double = pm.createNode('multDoubleLinear', name='jnt_{0}_stretch_mult'.format(index))
            mult_double.input1.set(jnt.tx.get() / arc_length)
            stretch_scale_mult.output >> mult_double.input2
            mult_double.output >> jnt.tx
            
        
        
        # create a y sine offset jnt
        sine_y_jnt = pm.createNode('joint', name='sine_y_{0}_jnt'.format(index), ss=True)
        sine_y_jnt.setMatrix(jnt.getMatrix(ws=True))
        pm.parent(sine_y_jnt, jnt)
        
        # create a z sine offset jnt
        sine_z_jnt = pm.createNode('joint', name='sine_z_{0}_jnt'.format(index), ss=True)
        sine_z_jnt.setMatrix(jnt.getMatrix(ws=True))
        pm.parent(sine_z_jnt, sine_y_jnt)
        
       
        # create the bind joints
        bind_jnt = pm.createNode('joint', name='bind_{0}_jnt'.format(index), ss=True)
        bind_jnt_list.append(bind_jnt)
        bind_jnt.setMatrix(jnt.getMatrix(ws=True))
        bind_jnt_grp = pm.group(em=True, name='bind_jnt_{0}_grp'.format(index))
        pm.parentConstraint(sine_z_jnt, bind_jnt_grp)
        pm.parent(bind_jnt, bind_jnt_grp)
        pm.parent(bind_jnt_grp, main_bind_jnt_grp)
        


        
        
        # setup the y sine animation
        
        # pma to offset the vary time input
        pma_sine_y = pm.createNode('plusMinusAverage', name='pma_sine_y{0}'.format(index))
        
        # connect root ctrl time attr to pma
        root_ctrl.time >> pma_sine_y.input1D[0]
        
        # connect the per joint offset to the pma
        pm.connectAttr('{0}.sine_y_offset{1}'.format(root_ctrl.longName(), index),  pma_sine_y.input1D[1])
            
        # create node cache
        cache_sine_y = pm.createNode('frameCache', name='frameCache_sine_y{0}_jnt'.format(index))
        
        # connect the pma offsetted time to varytime ant the attr to use as stream to the stream
        pma_sine_y.output1D >> cache_sine_y.varyTime
        root_ctrl.sineY >> cache_sine_y.stream
        
        # create a per joint scale to the sine
        sine_y_scale = pm.createNode('multDoubleLinear', name='sine_y_scale_{0}'.format(index))
        cache_sine_y.varying >> sine_y_scale.input1
        pm.connectAttr('{0}.sine_y_scale{1}'.format(root_ctrl.longName(), index), sine_y_scale.input2)
        
        # hook up the gloabal sacle to affect the per joint scale
        sine_y_global_scale_md = pm.createNode('multDoubleLinear', name='sine_y_global_scale_md_{0}'.format(index))       
        root_ctrl.sine_y_global_scale >> sine_y_global_scale_md.input1
        sine_y_scale.output >> sine_y_global_scale_md.input2
        
        # fianlly feed that into the jnt
        sine_y_global_scale_md.output >> sine_y_jnt.ty
        
        
        
        
        
        # setup the z sine animation
        
        # pma to offset the vary time input
        pma_sine_z = pm.createNode('plusMinusAverage', name='pma_sine_z{0}'.format(index))
        
        # connect root ctrl time attr to pma
        root_ctrl.time >> pma_sine_z.input1D[0]
        
        # connect the per joint offset to the pma
        pm.connectAttr('{0}.sine_z_offset{1}'.format(root_ctrl.longName(), index),  pma_sine_z.input1D[1])
            
        # create node cache
        cache_sine_z = pm.createNode('frameCache', name='frameCache_sine_z{0}_jnt'.format(index))
        
        # connect the pma offsetted time to varytime ant the attr to use as stream to the stream
        pma_sine_z.output1D >> cache_sine_z.varyTime
        root_ctrl.sineZ >> cache_sine_z.stream
        
        # create a per joint scale to the sine
        sine_z_scale = pm.createNode('multDoubleLinear', name='sine_z_scale_{0}'.format(index))
        cache_sine_z.varying >> sine_z_scale.input1
        pm.connectAttr('{0}.sine_z_scale{1}'.format(root_ctrl.longName(), index), sine_z_scale.input2)
        
        # hook up the gloabal sacle to affect the per joint scale
        sine_z_global_scale_md = pm.createNode('multDoubleLinear', name='sine_z_global_scale_md_{0}'.format(index))       
        root_ctrl.sine_z_global_scale >> sine_z_global_scale_md.input1
        sine_z_scale.output >> sine_z_global_scale_md.input2
        
        # fianlly feed that into the jnt
        sine_z_global_scale_md.output >> sine_z_jnt.tz
        
        
      
        
    
    # set key frames and handle the post curve behaviour
    
    # setup sine y animation
    pm.setKeyframe(root_ctrl, v=-1, attribute='sineY', t=0)
    pm.setKeyframe(root_ctrl, v=1, attribute='sineY', t=48)
    pm.setKeyframe(root_ctrl, v=-1, attribute='sineY', t=96)
    pm.setInfinity(root_ctrl, at='sineY', pri='cycleRelative', poi='cycleRelative')
    
    # setup sine z animation
    pm.setKeyframe(root_ctrl, v=-1, attribute='sineZ', t=0)
    pm.setKeyframe(root_ctrl, v=1, attribute='sineZ', t=24)
    pm.setKeyframe(root_ctrl, v=-1, attribute='sineZ', t=48)
    pm.setInfinity(root_ctrl, at='sineZ', pri='cycleRelative', poi='cycleRelative')
    
    
    # set keyframes of the time attr on the root ctrl, set naim curve properties   
    pm.setKeyframe(root_ctrl, v=0, attribute='time', t=0)
    pm.setKeyframe(root_ctrl, v=1, attribute='time', t=1)
    pm.setInfinity(root_ctrl, at='time', pri='cycleRelative', poi='cycleRelative')
    
    pm.keyTangent(root_ctrl, edit=True, attribute='time', itt='linear', ott='linear') 
    

    pm.select(deselect=True)
    bind_jnt_set = pm.sets(name='{0}_bind_joints'.format(name))
    bind_jnt_set.addMembers(bind_jnt_list)

  
    return ret_dict
        
        

    
#pm.select(['group1', 'group2', 'group3', 'group4'])
#pm.select(['group1', 'group2', 'group3'])
#pm.select(['group1'])

'''
pm.select(['flower_jnt_pos'])
sel_list = pm.ls(sl=True)
jnt_dict_list = build_joints(sel_list)
dyn_joint_dict_1 = setup_dynamic_joint_chain(jnt_dict_list[0])

'''

node = pm.PyNode('flower_jnt_pos')
ref_list = [node, node, node, node, node]

# build the joints
jnt_dict_list = build_joints(ref_list, name_list=['tendri_1', 'tendril_2', 'tendril_3', 'tendril_4', 'tendril_5'])

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

dyn_joint_dict_5 = setup_dynamic_joint_chain(jnt_dict_list[4], existing_hairsystem=hairsystem_1)
output_curve_list.append(dyn_joint_dict_5.get('output_curve'))


for output_curve in output_curve_list:
    curve_parent = output_curve.getParent()
    pm.parent(output_curve, output_curve_grp)
    pm.delete(curve_parent)
    


