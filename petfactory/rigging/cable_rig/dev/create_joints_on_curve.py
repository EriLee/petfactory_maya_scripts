import pymel.core as pm
import maya.api.OpenMaya as om
import petfactory.modelling.mesh.extrude_profile as pet_extrude
import petfactory.rigging.nhair.nhair_dynamics as nhair_dynamics
reload(pet_extrude)

pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)


def create_joints_on_curve(crv, num_joints, parent_joints=True, show_lra=True):
    
    crv_shape = crv.getShape()
    length = crv_shape.length()
    length_inc = length / (num_joints-1)
    
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
            up_vec = pm.datatypes.Vector(0,1,0)
            
            # if the aim and up vec are effectively (within a certain tolerance) colinear, the
            # resulting perpendicualar vector will not be vaild in this case the negative z axis
            # will be used as up vector
            if aim_vec.isParallel(up_vec, tol=0.1):
                
                up_vec = pm.datatypes.Vector(0,0,-1)
                
                cross_vec = aim_vec.cross(up_vec)
                up_vec_ortho = cross_vec.cross(aim_vec)
                tm = pm.datatypes.TransformationMatrix(    [aim_vec[0], aim_vec[1], aim_vec[2], 0],
                                                           [cross_vec[0], cross_vec[1], cross_vec[2], 0],
                                                           [up_vec_ortho[0], up_vec_ortho[1], up_vec_ortho[2], 0],
                                                           [prev_jnt[0], prev_jnt[1], prev_jnt[2], 1])            
            else:
                cross_vec = aim_vec.cross(up_vec)
                up_vec_ortho = cross_vec.cross(aim_vec)
                tm = pm.datatypes.TransformationMatrix(    [aim_vec[0], aim_vec[1], aim_vec[2], 0], 
                                                           [up_vec_ortho[0], up_vec_ortho[1], up_vec_ortho[2], 0],
                                                           [cross_vec[0], cross_vec[1], cross_vec[2], 0],
                                                           [prev_jnt[0], prev_jnt[1], prev_jnt[2], 1])
    
            #om_tm = om.MTransformationMatrix(om.MMatrix(tm))
            #r = om_tm.rotation()
            #r_deg = pm.util.degrees((r.x, r.y, r.z))
            #print(r_deg)
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
            
def add_cable_rig(crv, jnt_list):
    
    ret_dict = {}
    
    # organize
    main_cable_grp = pm.group(em=True, name='main_cable_grp')
    misc_grp = pm.group(em=True, name='misc_grp', parent=main_cable_grp)
    ctrl_grp = pm.group(em=True, name='ctrl_grp', parent=main_cable_grp)
    hidden_grp = pm.group(em=True, name='hidden_grp', parent=misc_grp)
    hidden_grp.visibility.set(False, lock=True)
    
    # create the ctrl
    start_ctrl = pm.circle(name='start_ctrl', normal=(1,0,0))[0]
    start_ctrl_grp = pm.group(em=True, name='start_ctrl_grp', parent=ctrl_grp)
    pm.parent(start_ctrl, start_ctrl_grp)
    
    end_ctrl = pm.circle(name='end_ctrl', normal=(1,0,0))[0]
    end_ctrl_grp = pm.group(em=True, name='end_ctrl_grp', parent=ctrl_grp)
    pm.parent(end_ctrl, end_ctrl_grp)
    
    start_ctrl_grp.setMatrix(jnt_list[0].getMatrix(worldSpace=True))
    end_ctrl_grp.setMatrix(jnt_list[-1].getMatrix(worldSpace=True))
    
    # duplicate the crv
    orig_crv = pm.duplicate(crv, name='orig_crv')[0]
    orig_crv_shape = orig_crv.getShape()
    num_cvs = orig_crv_shape.numCVs()
    
    result_crv = pm.duplicate(crv, name='result_crv')[0]
    orig_crv.worldSpace >> result_crv.create
    
    
    #-----------------
    # ik spline
    #-----------------
     
    #pm.duplicate(jnt_list[0])
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

    pm.parent(iks_handle, hidden_grp)  
    
    
    
    #-----------------
    # clusters
    #-----------------
    
    cluster_list = []
    for i in range(num_cvs):
     
        clust, clust_handle = pm.cluster('{0}.cv[{1}]'.format(orig_crv_shape.longName(), str(i)), relative=False, name='{0}_{1}_cluster_'.format('test', i))
        cluster_list.append(clust_handle)
        
    # parent the first and last clusters to ctrl   
    pm.parent(cluster_list[0], cluster_list[1], start_ctrl)
    pm.parent(cluster_list[-1], cluster_list[-2], end_ctrl)
    
    # parent the joint to the first ctrl
    pm.parent(jnt_list[0], start_ctrl)
    jnt_list[0].translate.set((0,0,0))
    
    # group and point constraint the mid cluster
    mid_clust_grp = pm.group(em=True, name='mid_cluster_grp')
    
    clust_pos = pm.xform(cluster_list[2], q=True, rotatePivot=True, ws=True)
    mid_clust_grp.translate.set(clust_pos)

    pm.pointConstraint(start_ctrl, end_ctrl, mid_clust_grp, mo=True)
    #pm.toggle(mid_clust_grp, la=True)
    pm.parent(cluster_list[2], mid_clust_grp)
    pm.parent(orig_crv, result_crv, mid_clust_grp, misc_grp)
    
    
    #-----------------
    # mesh
    #-----------------
    
    pm_mesh = add_mesh_to_joints(jnt_list)
    pm.parent(pm_mesh, misc_grp)
    
    
    #-----------------
    # stretch
    #-----------------
    
    # create a crv info, to get the arclength
    result_crv_info = pm.arclen(result_crv, ch=True)
    strecth_amount_md = pm.createNode('multiplyDivide', name='strecth_amount_md')
    strecth_amount_md.operation.set(2)
    result_crv_info.arcLength >> strecth_amount_md.input1X
    strecth_amount_md.input2X.set(result_crv_info.arcLength.get())
    
    for jnt in jnt_list:
        strecth_amount_md.outputX >> jnt.scaleX
        
    
    ret_dict['joint_list'] = jnt_list
    ret_dict['cluster_list'] = cluster_list
    ret_dict['result_crv'] = result_crv
    ret_dict['orig_crv'] = orig_crv
    ret_dict['start_ctrl'] = start_ctrl
    ret_dict['end_ctrl'] = end_ctrl
    
    return ret_dict
    
    

    
def add_mesh_to_joints(joint_list, cable_radius=.5, cable_axis_divisions=12):

    profile_pos = pet_extrude.create_profile_points(radius=cable_radius, axis_divisions=cable_axis_divisions, axis=0)
    
    extrude_pos_list = []
    for jnt in joint_list:
        tm = pm.datatypes.TransformationMatrix(jnt.getMatrix(ws=True))
        pos = pm.xform(jnt, ws=True, t=True, q=True)
        extrude_pos_list.append( [p.rotateBy(tm)+pos for p in profile_pos] )
        
    pm_mesh = pet_extrude.mesh_from_pos_list(pos_list=extrude_pos_list, name='cable_mesh', as_pm_mesh=True) 
    pm.skinCluster(jnt_list, pm_mesh, tsb=True)
    
    return pm_mesh


def make_cable_rig_dynamic(rig_dict, existing_hairsystem=None):
    
    ret_dict = {}
    
    orig_crv = rig_dict.get('orig_crv')
    result_crv = rig_dict.get('result_crv')
    start_ctrl = rig_dict.get('start_ctrl')

    #-----------------
    # add dynamics
    #-----------------
    
    nhair_dict_list = nhair_dynamics.make_curve_dynamic(orig_crv)
    
    ret_dict['output_curve'] = output_curve = nhair_dict_list.get('output_curve')
    ret_dict['follicle'] = follicle = nhair_dict_list.get('follicle')
    ret_dict['hairsystem'] = hairsystem = nhair_dict_list.get('hairsystem')
    ret_dict['nucleus'] = nucleus = nhair_dict_list.get('nucleus')
    
    # if we want to use an existing hair system
    if existing_hairsystem is not None:
        print('Delete current hairsystem, use {0}'.format(existing_hairsystem))
        
        num_connection = len(pm.listConnections('{0}.inputHair'.format(existing_hairsystem)))
        
        follicle.outHair >> existing_hairsystem.inputHair[num_connection]
        existing_hairsystem.outputHair[num_connection] >> follicle.currentPosition
        
        pm.delete(hairsystem)
        
    else:         
        hairsystem.startCurveAttract.set(0.005)
            
            
            
    
    # nucleus    
    if nucleus:
        nucleus.spaceScale.set(.1)

    pm.addAttr(start_ctrl, longName='dynamic_blendshape', minValue=0.0, maxValue=1.0, defaultValue=0.0, keyable=True)
    blendshape = pm.blendShape(output_curve, result_crv, origin='world')[0]
    start_ctrl.dynamic_blendshape >> blendshape.weight[0] 
    

#crv = pm.curve(d=3, p=[(0,0,0), (0,5,0), (0,10,0), (0,15,0), (0,15,5)])
#crv = pm.ls(sl=True)[0]
crv = pm.PyNode('curve1')    
#pm.toggle(crv, hull=True)

# build the joints on curve
jnt_list = create_joints_on_curve(crv, num_joints=10)

cable_rig_dict = add_cable_rig(crv, jnt_list)

make_cable_rig_dynamic(cable_rig_dict)

#add_mesh_to_joints(jnt_list)


