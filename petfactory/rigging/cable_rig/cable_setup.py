import pymel.core as pm
import maya.api.OpenMaya as om
import petfactory.modelling.mesh.extrude_profile as pet_extrude
import petfactory.rigging.nhair.nhair_dynamics as nhair_dynamics


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
                
                up_vec = pm.datatypes.Vector(0,0,1)
                
                cross_vec = aim_vec.cross(up_vec)
                up_vec_ortho = cross_vec.cross(aim_vec)
                tm = pm.datatypes.TransformationMatrix(    [aim_vec[0], aim_vec[1], aim_vec[2], 0],
                                                           [up_vec_ortho[0], up_vec_ortho[1], up_vec_ortho[2], 0],
                                                           [cross_vec[0], cross_vec[1], cross_vec[2], 0],                                                   
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
            
def add_cable_rig(crv, jnt_list, name):
    
    ret_dict = {}
    num_joints = len(jnt_list)
    
    # organize
    main_cable_grp = pm.group(em=True, name='{0}_main_rig_grp'.format(name))
    misc_grp = pm.group(em=True, name='misc_grp', parent=main_cable_grp)
    ctrl_grp = pm.group(em=True, name='ctrl_grp', parent=main_cable_grp)
    hidden_grp = pm.group(em=True, name='hidden_grp', parent=misc_grp)
    hidden_grp.visibility.set(False, lock=True)
    bind_jnt_main_grp = pm.group(em=True, name='bind_jnt_main_grp', parent=main_cable_grp)

    # create the ctrl
    start_ctrl = pm.circle(name='{0}_start_ctrl'.format(name), normal=(1,0,0))[0]
    start_ctrl_grp = pm.group(em=True, name='{0}_start_ctrl_grp'.format(name), parent=ctrl_grp)
    pm.parent(start_ctrl, start_ctrl_grp)
    
    end_ctrl = pm.circle(name='{0}_end_ctrl'.format(name), normal=(1,0,0))[0]
    end_ctrl_grp = pm.group(em=True, name='{0}_end_ctrl_grp'.format(name), parent=ctrl_grp)
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
    cluster_zero_grp_list = []
    for i in range(num_cvs):
     
        clust, clust_handle = pm.cluster('{0}.cv[{1}]'.format(orig_crv_shape.longName(), str(i)), relative=False, name='{0}_{1}_cluster_'.format('test', i))
        cluster_list.append(clust_handle)
        
        # create a group to zero out the transformation
        cluster_zero_grp_list.append(pm.group(em=True))
        pm.parent(clust_handle, cluster_zero_grp_list[i])
                
        
    # parent the first and last clusters to ctrl   
    pm.parent(cluster_zero_grp_list[0], cluster_zero_grp_list[1], start_ctrl)
    pm.parent(cluster_zero_grp_list[-1], cluster_zero_grp_list[-2], end_ctrl)
    
    # parent the joints > jnt_grp, jnt_grp > start_ctrl
    jnt_grp = pm.group(em=True, name='jnt_grp')
    #jnt_grp.visibility.set(False)
    jnt_grp.setMatrix(jnt_list[0].getMatrix(worldSpace=True))
    pm.parent(jnt_list[0], jnt_grp)
    # set the translation and rotation of first jnt to 0
    jnt_list[0].translate.set((0,0,0))
    jnt_list[0].rotate.set((0,0,0))
    pm.parent(jnt_grp, start_ctrl)
    

    # group and point constraint the mid cluster
    mid_clust_grp = pm.group(em=True, name='mid_cluster_grp')
    
    clust_pos = pm.xform(cluster_list[2], q=True, rotatePivot=True, ws=True)
    mid_clust_grp.translate.set(clust_pos)

    pm.pointConstraint(start_ctrl, end_ctrl, mid_clust_grp, mo=True)

    pm.parent(cluster_zero_grp_list[2], mid_clust_grp)
    pm.parent(orig_crv, result_crv, hidden_grp)
    pm.parent(mid_clust_grp, misc_grp)
    #pm.parent(orig_crv, result_crv, mid_clust_grp, misc_grp)
    
    
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
        
    
    
    
    
    #-----------------
    # add bind joints
    #-----------------
    
    bind_joint_list = []
    for index, jnt in enumerate(jnt_list):
        bind_jnt = pm.createNode('joint', name='bind_joint_{0}'.format(index), ss=True)
        bind_joint_list.append(bind_jnt)
        bind_jnt_grp = pm.group(em=True, name='bind_joint_grp{0}'.format(index))
        pm.parent(bind_jnt, bind_jnt_grp)
        bind_jnt_grp.setMatrix(jnt.getMatrix(ws=True))
        pm.parent(bind_jnt_grp, bind_jnt_main_grp)
        
        '''
        # contstrain the first bind jnt to the start ctrl
        if index is 0:
            pm.parentConstraint(start_ctrl, bind_jnt_grp)
            
        # contstrain the first bind jnt to the start ctrl            
        elif index is num_joints-1:
            pm.parentConstraint(end_ctrl, bind_jnt_grp)
            
        # else constrain to the regular joints
        else:
            pm.parentConstraint(jnt, bind_jnt_grp)
        '''
        
        # to avoid the last jnt to "go past" the end ctrl, we get the pos
        # from the end ctrl and the orienttation from the jnt
        if index is num_joints-1:
            pm.pointConstraint(end_ctrl, bind_jnt_grp)
            pm.orientConstraint(jnt, bind_jnt_grp)
            
        else:
            pm.parentConstraint(jnt, bind_jnt_grp)
    
    
    ret_dict['joint_list'] = jnt_list
    ret_dict['bind_joint_list'] = bind_joint_list
    ret_dict['cluster_list'] = cluster_list
    ret_dict['result_crv'] = result_crv
    ret_dict['orig_crv'] = orig_crv
    ret_dict['start_ctrl'] = start_ctrl
    ret_dict['end_ctrl'] = end_ctrl
    ret_dict['misc_grp'] = misc_grp
    
    return ret_dict
    
    

    
def add_mesh_to_joints(joint_list, cable_radius=.5, cable_axis_divisions=12):

    profile_pos = pet_extrude.create_profile_points(radius=cable_radius, axis_divisions=cable_axis_divisions, axis=0)
    
    extrude_pos_list = []
    for jnt in joint_list:
        tm = pm.datatypes.TransformationMatrix(jnt.getMatrix(ws=True))
        pos = pm.xform(jnt, ws=True, t=True, q=True)
        extrude_pos_list.append( [p.rotateBy(tm)+pos for p in profile_pos] )
        
    pm_mesh = pet_extrude.mesh_from_pos_list(pos_list=extrude_pos_list, name='cable_mesh', as_pm_mesh=True) 
    pm.skinCluster(joint_list, pm_mesh, tsb=True)
    
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
    
    
    output_curve.getShape().overrideDisplayType.set(2)
    return ret_dict
    

def set_hairsystem_properties(hairsystem):
    
    hairsystem.attractionScale[0].attractionScale_Position.set(0.2)
    hairsystem.attractionScale[0].attractionScale_FloatValue.set(1)
    
    hairsystem.attractionScale[1].attractionScale_Position.set(0.5)
    hairsystem.attractionScale[1].attractionScale_FloatValue.set(0.1)
    
    hairsystem.attractionScale[2].attractionScale_Position.set(.8)
    hairsystem.attractionScale[2].attractionScale_FloatValue.set(1)
    
    hairsystem.startCurveAttract.set(0.5)
    hairsystem.damp.set(0.5)

def setup_selected_curves(sel_list):
    
    # create output crv grp
    output_crv_grp = pm.group(em=True, name='output_curve_grp')
    pm.select(deselect=True)
    
    # create sets for ctrl and mesh
    cable_rig_ctrl_set = pm.sets(name='cable_rig_ctrl_set')
    cable_mesh_set = pm.sets(name='cable_mesh_set')
        
    for index, crv in enumerate(sel_list):
        
        # build the joints on curve
        jnt_list = create_joints_on_curve(crv, num_joints=5)
        
        # create the cable rig
        cable_rig_dict = add_cable_rig(crv, jnt_list, name='cable_rig_{0}'.format(index))
        misc_grp = cable_rig_dict.get('misc_grp')
        
        # add to ctrl set
        cable_rig_ctrl_set.add(cable_rig_dict.get('start_ctrl'))
        
        # make dynamic
        # get a reference to the first hairsystem
        if index is 0:
            dynamic_dict = make_cable_rig_dynamic(cable_rig_dict)
            existing_hairsystem = dynamic_dict.get('hairsystem')
        
        # pass the second hairsystem to the other rig setup defs          
        else:
            dynamic_dict = make_cable_rig_dynamic(cable_rig_dict, existing_hairsystem=existing_hairsystem)
        
        # get a ref to the output crv, reparent and delete the old group
        output_crv = dynamic_dict.get('output_curve')
        output_crv_parent = output_crv.getParent()
        pm.parent(output_crv, output_crv_grp)
        pm.delete(output_crv_parent)
        
        # get the bind joint list
        bind_jnt_list = cable_rig_dict.get('bind_joint_list')

        # add mesh, parent and add to set
        pm_mesh = add_mesh_to_joints(bind_jnt_list)
        pm.parent(pm_mesh, misc_grp)
        cable_mesh_set.add(pm_mesh)
    
    # set hairsystem properties, select the hairsystem (convenience) so we can inspect the properties
    pm.select(existing_hairsystem)
    set_hairsystem_properties(existing_hairsystem)



#pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)
#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/3deg_5cvs.mb', f=True)


#crv = pm.curve(d=3, p=[(0,0,0), (0,5,0), (0,10,0), (0,15,0), (0,15,5)])
#crv = pm.ls(sl=True)[0]
#crv = pm.PyNode('curve1')    
#pm.toggle(crv, hull=True)

#sel_list = pm.ls(sl=True)
#sel_list = [pm.PyNode('curve{0}'.format(n)) for n in range(4)]
#sel_list.append(pm.PyNode('curve1'))
#sel_list.append(pm.PyNode('curve2'))

# setup joints
#jnt_list = create_joints_on_curve(sel_list[0], num_joints=10)

# create the base rig
#cable_rig_dict = add_cable_rig(crv=sel_list[0], jnt_list=jnt_list, name='cable_rig_{0}'.format(index))
#create_joints_on_curve(sel_list[1], num_joints=10)
    
#setup_selected_curves(sel_list)



