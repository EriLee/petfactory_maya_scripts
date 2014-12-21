import pymel.core as pm
import petfactory.rigging.nhair.nhair_dynamics as nhair_dynamics


def setup_cable(num_joints, existing_hairsystem=None):

    ret_dict = {}
    
    main_cable_grp = pm.group(em=True, name='main_cable_grp')
    misc_grp = pm.group(em=True, name='misc_grp', parent=main_cable_grp)
    hidden_grp = pm.group(em=True, name='hidden_grp', parent=misc_grp)
    hidden_grp.visibility.set(False, lock=True)
    
    #num_joints = 10
    jnt_list = []
    
    # the crv, should be 3 degree, with 5 cvs
    crv = pm.curve(name='orig_crv', d=3, ep=[(-5, 0, 0), (0, 0, 0), (5, 0, 0)])
    
    
    result_crv = pm.duplicate(crv, name='result_crv')[0]
    crv.worldSpace >> result_crv.create
    
    # create a crv info, to get the arclength
    result_crv_info = pm.arclen(result_crv, ch=True)
    strecth_amount_md = pm.createNode('multiplyDivide', name='strecth_amount_md')
    strecth_amount_md.operation.set(2)
    result_crv_info.arcLength >> strecth_amount_md.input1X
    strecth_amount_md.input2X.set(result_crv_info.arcLength.get())
    
    
    # create and position the start and end ctrl
    start_ctrl = pm.circle(normal=(1,0,0), name='start')[0]
    end_ctrl = pm.circle(normal=(1,0,0), name='end')[0]
    
    # add attr to start ctrl
    pm.addAttr(start_ctrl, longName='stretch_scale', defaultValue=1.0, keyable=True)
    pm.addAttr(start_ctrl, longName='dynamic_blendshape', minValue=0.0, maxValue=1.0, defaultValue=0.0, keyable=True)
    #pm.addAttr(start_ctrl, longName='Mode', at="enum", en="Static:Dynamic", keyable=True)
    
    
    # get the max u value
    crv_shape = crv.getShape()
    num_cvs = crv_shape.numCVs()
    min_u, max_u = crv_shape.getKnotDomain()
    
    # get a u value increment from start to end
    u_inc = max_u / (num_joints-1)
    jnt_list = []
    
    for index in range(num_joints):
        
        pos = crv_shape.getPointAtParam(u_inc * index, space='world')
    
        # create the joints
        jnt = pm.createNode('joint', name='jnt_{0}'.format(index), ss=True)
        jnt_list.append(jnt)
        jnt.translate.set(pos)
        strecth_amount_md.outputX >> jnt.scaleX
        #pm.toggle(jnt, localAxis=True)
        
        # parent the jnt
        if index > 0:
            pm.parent(jnt, jnt_list[index-1])
        
        
    
    start_ctrl.setMatrix(jnt_list[0].getMatrix(ws=True))
    end_ctrl.setMatrix(jnt_list[-1].getMatrix(ws=True))
    
    
    # create the ikSpline
    iks_handle, effector = pm.ikHandle(solver='ikSplineSolver', curve=result_crv, parentCurve=False, createCurve=False, rootOnCurve=False, twistType='easeInOut', sj=jnt_list[0], ee=jnt_list[-1])
    
    # enable the advanced twist controls
    iks_handle.dTwistControlEnable.set(1)
    
    # set world up type to object rotation up (start/end)
    iks_handle.dWorldUpType.set(4)
    
    # set the up axis to +z
    iks_handle.dWorldUpAxis.set(3)
    
    # set the up vector and up vector 2 to z
    iks_handle.dWorldUpVector.set(0,0,1)
    iks_handle.dWorldUpVectorEnd.set(0,0,1)
    
    
    # set the world up objects
    start_ctrl.worldMatrix[0] >> iks_handle.dWorldUpMatrix
    end_ctrl.worldMatrix[0] >> iks_handle.dWorldUpMatrixEnd
    
    
    # add cluster to cvs. The first cluster will have first and second cv the mid cv will have one
    # cluster to it self and the last cluster will have to cvs.
    cluster_list = []
    for i in range(num_cvs):
     
        clust, clust_handle = pm.cluster('{0}.cv[{1}]'.format(crv_shape.longName(), str(i)), relative=False, name='{0}_{1}_cluster_'.format('test', i))
        cluster_list.append(clust_handle)
        
        
    
    # make the nhair_target_crv dynamic
    
    nhair_dict = nhair_dynamics.make_curve_dynamic(crv)
    output_curve = nhair_dict.get('output_curve')
    follicle = nhair_dict.get('follicle')
    nucleus = nhair_dict.get('nucleus')
    hairsystem = nhair_dict.get('hairsystem')
        
    if nucleus:
        nucleus.spaceScale.set(.1)
        ret_dict['nucleus'] = nucleus
               
    if follicle:
        follicle_parent = follicle.getParent()
        pm.parent(follicle, misc_grp)
        pm.delete(follicle_parent)
        ret_dict['follicle'] = follicle
        
    if output_curve:
        ret_dict['output_curve'] = output_curve
    
    # if we want to use an existing hair system
    if existing_hairsystem is not None:
        print('Delete current hairsystem, use {0}'.format(existing_hairsystem))
        
        num_connection = len(pm.listConnections('{0}.inputHair'.format(existing_hairsystem)))
        
        follicle.outHair >> existing_hairsystem.inputHair[num_connection]
        existing_hairsystem.outputHair[num_connection] >> follicle.currentPosition
        
        pm.delete(hairsystem)
        
    else:         
        hairsystem.startCurveAttract.set(0.005)
        
            
    blendshape_dynamic = pm.blendShape(output_curve, result_crv, origin='world', weight=(0,0))[0]
    start_ctrl.dynamic_blendshape >> blendshape_dynamic.weight[0]
    

        
    # parent the first and last clusters to ctrl   
    pm.parent(cluster_list[0], cluster_list[1], start_ctrl)
    pm.parent(cluster_list[-1], cluster_list[-2], end_ctrl)
    
    # parent the joint to the first ctrl
    pm.parent(jnt_list[0], start_ctrl)
    
    mid_clust_grp = pm.group(em=True, name='mid_cluster_grp')
    pm.parent(cluster_list[2], mid_clust_grp)
    pm.pointConstraint(start_ctrl, end_ctrl, mid_clust_grp)
    
    
    pm.parent(start_ctrl, end_ctrl, main_cable_grp)
    pm.parent(mid_clust_grp, misc_grp)
    
    pm.parent(iks_handle, hidden_grp)
    pm.parent(result_crv, misc_grp)
    
    
    return ret_dict

pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)

output_curve_grp = pm.group(em=True, name='output_curve_grp')
cable_dict = setup_cable(10)

output_curve = cable_dict.get('output_curve')
output_curve_parent = output_curve.getParent()
pm.parent(output_curve, output_curve_grp)
pm.delete(output_curve_parent)
