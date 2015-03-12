import pymel.core as pm
import petfactory.util.vector as pet_vector
import petfactory.rigging.ctrl.ctrl as pet_ctrl
import petfactory.modelling.mesh.extrude_profile as pet_extrude

'''
TODO

add attr to start and end ctrl to control the blend

'''

def create_joints_on_axis(num_joints=10, parent_joints=False, show_lra=True, name='joint', spacing=1, axis=0):
    
    jnt_list = []
    for index in range(num_joints):
        
        jnt = pm.createNode('joint', name='{0}_{1}_jnt'.format(name, index), ss=True)
        pos = (spacing*index, 0, 0)
        jnt.translate.set(pos)
        jnt_list.append(jnt)
        
        if show_lra:
            pm.toggle(jnt, localAxis=True)
            
    
    if parent_joints:
        parent_joint_list(jnt_list)
    
    return jnt_list
    
def create_joints_on_curve(crv, num_joints, up_axis, parent_joints=True, show_lra=True, name='joint', start_offset=0, end_offset=0):
    
    crv_shape = crv.getShape()
    crv_length = crv_shape.length()
    
    length = crv_length * (1.0-start_offset-end_offset)
    length_inc = length / (num_joints-1)
    start_length_offset = crv_length * start_offset
    
    crv_matrix = crv.getMatrix(worldSpace=True) 
    up_vec = pm.datatypes.Vector(crv_matrix[up_axis][0], crv_matrix[up_axis][1], crv_matrix[up_axis][2])
    up_vec.normalize()
    
    
    jnt_list = []
    for index in range(num_joints):
        
        u = crv_shape.findParamFromLength(length_inc*index+start_length_offset)
        p = crv_shape.getPointAtParam(u, space='world')
        jnt = pm.createNode('joint', name='{0}_{1}_jnt'.format(name, index), ss=True)
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
                
                
    if parent_joints:
        parent_joint_list(jnt_list)
    
    return jnt_list
            
            
def parent_joint_list(joint_list):         
    for index, jnt in enumerate(joint_list):
        if index > 0:
            pm.parent(joint_list[index], joint_list[index-1])
    pm.select(deselect=True)
    

def cable_base_ik(crv, num_joints, name='curve_rig', up_axis=2, pv_dir=1):
        
    crv_shape = crv.getShape()
    num_cvs = crv_shape.numCVs()

    cvs_per_bone = float(num_cvs - num_joints) / (num_joints-1)
    min_cv_count = num_joints + (num_joints-1)
    
    # check if the number of cvs are valid
    if num_cvs >= min_cv_count and cvs_per_bone % 1 == 0:
        print('valid number of cvs')
    
    else:
        pm.warning('The number of cvs must be at least {0} and follow pattern num_jnt+(num_jnt-1)*n where n is positive integer'.format(min_cv_count))
        return
        
        
    # duplicate the crv, freeze transform, keep the position
    crv = pm.duplicate(crv, n='{0}_cubic_crv'.format(name))[0]
    pm.makeIdentity(crv, apply=True)
    crv_shape = crv.getShape()
    
        
    num_linear_crv_div = (num_cvs - 3) / 2    
    min_u, max_u = crv_shape.getKnotDomain()
    
    # get the up axis from the crv matrix, used to create a transform matrix for the start / end ctrl
    crv_matrix = crv.getMatrix(worldSpace=True)
    up_vec = pm.datatypes.Vector(crv_matrix[up_axis][0], crv_matrix[up_axis][1], crv_matrix[up_axis][2])
    up_vec.normalize()
    
    # position the main grp and position it
    main_grp = pm.group(em=True, n='{0}_main_grp'.format(name))
    main_grp_pos = crv_shape.getPointAtParam(0, space='world')
    main_grp.translate.set(main_grp_pos)
    
    # organize, create groups
    ctrl_grp = pm.group(em=True, parent=main_grp, n='{0}_ctrl_grp'.format(name))
    bind_geo_grp = pm.group(em=True, parent=main_grp, n='{0}_bind_geo_grp'.format(name))
    hidden_grp = pm.group(em=True, parent=main_grp, n='{0}_hidden_grp'.format(name))
    start_ctrl_hidden_grp = pm.group(em=True, n='{0}_start_ctrl_hidden_grp'.format(name))
    end_ctrl_hidden_grp = pm.group(em=True, n='{0}_end_ctrl_hidden_grp'.format(name))
    

    # create the ik joints
    ik_jnt_list = create_joints_on_curve(crv=crv, num_joints=num_joints, up_axis=2, parent_joints=True, show_lra=True, name='{0}_base_ik'.format(name))
    
    # calculate the start and end t matrix
    start_matrix = matrix_from_u(crv=crv, start_u=0, end_u=.05, pos_u=0, up_vec=up_vec)
    end_matrix = matrix_from_u(crv=crv, start_u=max_u-.05, end_u=max_u, pos_u=max_u, up_vec=up_vec)
    
    #start_jnt = pm.createNode('joint', name='{0}_start_ctrl_jnt'.format(name), ss=True)
    #start_jnt.setMatrix(start_matrix)
    
    #end_jnt = pm.createNode('joint', name='{0}_end_ctrl_jnt'.format(name), ss=True)
    #end_jnt.setMatrix(end_matrix)
    
    # create start and end ctrl
    ctrl_start = pet_ctrl.CreateCtrl.create_circle_arrow(name='start_ctrl', size=1)
    ctrl_start.setMatrix(start_matrix)
    
    ctrl_end = pet_ctrl.CreateCtrl.create_circle_arrow(name='end_ctrl', size=1)
    ctrl_end.setMatrix(end_matrix)
   
    # build the linear curve 
    jnt_pos_list = [ jnt.getTranslation(space='world') for jnt in ik_jnt_list ]
    pos_list = interpolate_positions(pos_list=jnt_pos_list, num_divisions=int(cvs_per_bone))
    
    
    # build the linear blendshape crv    
    crv_linear = pm.curve(d=3, p=pos_list, n='{0}_linear_crv'.format(name))

    
    # bind, add ik handle  
    ik_handle_unicode, ik_effector_unicode = pm.ikHandle(sj=ik_jnt_list[0], ee=ik_jnt_list[-1], n='{0}_ikh'.format(name), solver='ikRPsolver')
    # since tpm.ikHandle returns unicode and not a PyNode, we need to construct one here
    ik_handle = pm.PyNode('|{0}'.format(ik_handle_unicode))
    ik_effector = pm.PyNode('{0}'.format(ik_effector_unicode))
    
    
    
    
    dist = pm.distanceDimension(sp=ik_jnt_list[0].getTranslation(space='world'), ep=ik_jnt_list[-1].getTranslation(space='world'))
    dist_transform = dist.getParent()
    dist_transform.rename('{0}_dist'.format(name))
    start_loc = pm.listConnections( '{0}.startPoint'.format(dist))[0]
    start_loc.rename('start_loc')
    end_loc = pm.listConnections( '{0}.endPoint'.format(dist))[0]
    end_loc.rename('end_loc')
    
    
    
    linear_blendshape_RMV = pm.createNode('remapValue', name='linear_blendshape_RMV')
    
    crv_length = pm.arclen(crv)
    
    # get the length of the joint chain by getting the tx of the second to last jnt
    # I slice the ik_jnt_list to skip the first jnt
    jont_chain_length = 0  
    for jnt in ik_jnt_list[1:]:
        jont_chain_length += jnt.tx.get()
        
        
    dist.distance >> linear_blendshape_RMV.inputValue
    
    # set the min to 90 percent of the crv length, max to crv length
    linear_blendshape_RMV.inputMin.set(jont_chain_length*.8)
    linear_blendshape_RMV.inputMax.set(crv_length)
    
    # set the first value point to use a spline interpolation
    linear_blendshape_RMV.value[0].value_Interp.set(3)
    
        
    
    # set up the condition node
    jnt_cable_rig_stretch_CND = pm.createNode('condition', name='jnt_cable_rig_stretch_CND')
    jnt_cable_rig_stretch_MD = pm.createNode('multiplyDivide', name='jnt_cable_rig_stretch_MD')
    
    dist.distance >> jnt_cable_rig_stretch_MD.input1X
    jnt_cable_rig_stretch_MD.input2X.set(jont_chain_length)
    jnt_cable_rig_stretch_MD.operation.set(2)
    
    jnt_cable_rig_stretch_MD.outputX >> jnt_cable_rig_stretch_CND.colorIfTrueR
    
    dist.distance >> jnt_cable_rig_stretch_CND.firstTerm
    jnt_cable_rig_stretch_CND.operation.set(2)
    jnt_cable_rig_stretch_CND.secondTerm.set(jont_chain_length)
    
    jnt_cable_rig_stretch_CND.colorIfFalseR.set(1)
    
    # hook up stretch scaling of the jnts
    for jnt in ik_jnt_list[:-1]:
        jnt_cable_rig_stretch_CND.outColorR >> jnt.scaleX

    
    # create the blendshape
    blendshape_linear = pm.blendShape(crv_linear, crv, origin='local')[0]
    
    # set the blendshape weight to 1 (weighted to the linear crv) when we bind the crv
    # this will ensure that we get the correct deformation when the crv is stretched
    # if we do not do this the cvs will be slighlty off (maya bug?)
    #blendshape_linear.linear_curve_bs.set(1.0)
    blendshape_linear.weight[0].set(1.0)

    
    pm.skinCluster(ik_jnt_list[0], crv)
    
    # connect the remap out value to control the blendshape
    #linear_blendshape_RMV.outValue >> blendshape_linear.linear_curve_bs
    linear_blendshape_RMV.outValue >> blendshape_linear.weight[0]
    
    # pole vector
    pole_vector_target = pm.spaceLocator()
    
    pole_vector_target_grp = pm.group(em=True, n='polevector_target_grp')    
    pm.parent(pole_vector_target, pole_vector_target_grp)
    pole_vector_target.rename('pv_target_loc')

    
    pole_vector_target_grp.setMatrix(ik_jnt_list[0].getMatrix(worldSpace=True))
    pole_vector_target.tz.set(10)
    
    polevector_const = pm.poleVectorConstraint(pole_vector_target, ik_handle)
    # multiply by pv_dir
    ik_handle.twist.set(90*pv_dir)
    
    
    # organize
    pm.parent(ctrl_start, ctrl_end, ctrl_grp)
    pm.parent(dist_transform, pole_vector_target_grp, crv_linear, hidden_grp)
    pm.parent(crv, bind_geo_grp)
    
    pm.parent(start_ctrl_hidden_grp, ctrl_start)
    pm.parent(end_ctrl_hidden_grp, ctrl_end)
    
    pm.parent(start_loc, ik_jnt_list[0], start_ctrl_hidden_grp)
    pm.parent(ik_handle, end_loc, end_ctrl_hidden_grp)
    
    
    # uncheck inherit transform on cubic crv
    crv.inheritsTransform.set(0)
    
    # hide grp
    pm.setAttr(hidden_grp.v, 0, lock=True)
    pm.setAttr(start_ctrl_hidden_grp.v, 0, lock=True)
    pm.setAttr(end_ctrl_hidden_grp.v, 0, lock=True)
    
    crv_shape.overrideEnabled.set(1)
    crv_shape.overrideDisplayType.set(2)
    
    ret_dict = {}
    ret_dict['start_ctrl'] = ctrl_start
    ret_dict['end_ctrl'] = ctrl_end
    ret_dict['curve_cubic'] = crv
    ret_dict['curve_linear'] = crv_linear
    ret_dict['remap_value'] = linear_blendshape_RMV
    ret_dict['main_grp'] = main_grp
    #ret_dict['polevector'] = pole_vector_target
    
    return ret_dict

    
  
def matrix_from_u(crv, start_u, end_u, pos_u, up_vec):
    
    crv_shape = crv.getShape()
    
    start_p = crv_shape.getPointAtParam(start_u, space='world')
    end_p = crv_shape.getPointAtParam(end_u, space='world')
    pos_p = crv_shape.getPointAtParam(pos_u, space='world')
    
    aim_vec = end_p - start_p
    
    tm = pet_vector.remap_aim_up(aim_vec, up_vec, aim_axis=0, up_axis=2, invert_aim=False, invert_up=False, pos=pos_p)
    return tm
    
    
def mesh_from_start_end(start_joint, end_joint, length_divisions=10, cable_radius=.5, cable_axis_divisions=12):

    profile_pos = pet_extrude.create_profile_points(radius=cable_radius, axis_divisions=cable_axis_divisions, axis=0)
   
    start_pos = pm.datatypes.Vector(pm.xform(start_joint, ws=True, t=True, q=True))
    end_pos = pm.datatypes.Vector(pm.xform(end_joint, ws=True, t=True, q=True))
    distance = (end_pos - start_pos).length()
    length_inc = distance / (length_divisions-1)
    
    extrude_pos_list = []
    for i in range(length_divisions):
        tm = pm.datatypes.TransformationMatrix(start_joint.getMatrix(ws=True))
        pos = pm.datatypes.Vector(i*length_inc,0,0)
        extrude_pos_list.append( [p.rotateBy(tm)+pos for p in profile_pos] )
        
    pm_mesh = pet_extrude.mesh_from_pos_list(pos_list=extrude_pos_list, name='cable_mesh', as_pm_mesh=True) 

    return pm_mesh
    
    
def interpolate_positions(pos_list, num_divisions=1):
    
    u_inc = 1.0 / (num_divisions+1)
    last_index = len(pos_list)-1
    
    ret_pos_list = []
    for index, pos in enumerate(pos_list):
        
        if index < last_index:
            
            dx = pos_list[index+1][0] - pos_list[index][0]
            dy = pos_list[index+1][1] - pos_list[index][1]
            dz = pos_list[index+1][2] - pos_list[index][2]
            
            for u in range(num_divisions+1):
                ret_pos_list.append((   pos_list[index][0] + dx*u*u_inc,
                                        pos_list[index][1] + dy*u*u_inc,
                                        pos_list[index][2] + dz*u*u_inc))
    
        else:
            ret_pos_list.append(pos_list[-1])
    
    return ret_pos_list
    

def ctrl_joint_position_blend(ctrl, ctrl_local_position, point_on_crv_info, attr_name):
    
    # get a reference to the attr to control the blend color node
    blend_attr = pm.Attribute('{0}.{1}'.format(ctrl, attr_name))
    
    vector_prod = pm.createNode('vectorProduct')
    # set to point matrix product
    vector_prod.operation.set(4)
    # set the position
    vector_prod.input1.set(ctrl_local_position)
    ctrl.worldMatrix[0] >> vector_prod.matrix
    
    blend_col = pm.createNode('blendColors')
    blend_attr >> blend_col.blender
    vector_prod.output >> blend_col.color1
    point_on_crv_info.position >> blend_col.color2
    
    return blend_col
    
def add_cable_bind_joints(crv, name, num_ik_joints, num_bind_joints, show_lra=True, pv_dir=1):
    
    blender_attr_name_list = ['one', 'two', 'three']
    blender_value_list = [.7, .4, .1]
        
    cable_base_dict = cable_base_ik(crv=crv, num_joints=num_ik_joints, name=name, pv_dir=pv_dir)
    
    cubic_crv = cable_base_dict['curve_cubic']
    linear_crv = cable_base_dict['curve_linear']
    start_ctrl = cable_base_dict['start_ctrl']
    end_ctrl = cable_base_dict['end_ctrl']
    linear_blendshape_RMV = cable_base_dict['remap_value']
    main_grp = cable_base_dict['main_grp']

    for index, attr_name in enumerate(blender_attr_name_list):
        
        pm.addAttr(start_ctrl, longName=attr_name, keyable=True, defaultValue=blender_value_list[index])
        pm.addAttr(end_ctrl, longName=attr_name, keyable=True, defaultValue=blender_value_list[index])

        
    bind_jnt_grp = pm.group(em=True, parent=main_grp, n='{0}_bind_jnt_grp'.format(name))
    geo_grp = pm.group(em=True, parent=main_grp, n='{0}_geo_grp'.format(name))
        
    linear_crv_shape = linear_crv.getShape()
    linear_crv_min_u, linear_crv_max_u = linear_crv_shape.getKnotDomain()
    linear_curve_length = linear_crv_shape.length()
    
    cubic_crv_shape = cubic_crv.getShape()
    cubic_crv_min_u, cubic_crv_max_u = cubic_crv_shape.getKnotDomain()
    cubic_curve_length = cubic_crv_shape.length()
    
    # build the cable joints
    joint_list = create_joints_on_axis(num_joints=num_bind_joints, show_lra=show_lra)
    
    # create the mesh
    cable_mesh = mesh_from_start_end(start_joint=joint_list[0], end_joint=joint_list[-1], length_divisions=(num_bind_joints*2)-1)
    
    pm.skinCluster(joint_list, cable_mesh, toSelectedBones=True, ignoreHierarchy=True, skinMethod=2, maximumInfluences=3)
    
    
    cubic_length_inc = cubic_curve_length / (num_bind_joints-1)
    linear_length_inc = linear_curve_length / (num_bind_joints-1)

    
    #print(cubic_length_inc)
    for index, jnt in enumerate(joint_list):
        
        point_on_crv_info = pm.createNode('pointOnCurveInfo', name='point_on_crv_{0}'.format(index))
        point_on_crv_info.turnOnPercentage.set(True)
        cubic_crv_shape.worldSpace >> point_on_crv_info.inputCurve
        
        u_cubic = cubic_crv_shape.findParamFromLength(cubic_length_inc*index) / cubic_crv_max_u
        u_linear = linear_crv_shape.findParamFromLength(linear_length_inc*index) / linear_crv_max_u

        blend = pm.createNode('blendTwoAttr')
        blend.input[0].set(u_cubic)
        blend.input[1].set(u_linear)
        blend.output >> point_on_crv_info.parameter
        linear_blendshape_RMV.outValue >> blend.attributesBlender
        

        # blend the position of the jnt [1] - [3]
        if index > 0 and index <4:
            
            # blend the jnt positions            
            blend_col = ctrl_joint_position_blend(  ctrl=start_ctrl,
                                                    ctrl_local_position=(linear_length_inc*index,0,0),
                                                    point_on_crv_info=point_on_crv_info,
                                                    attr_name=blender_attr_name_list[index-1])

            blend_col.output >> jnt.translate
        
        # blend the position of the jnt [-4] - [-2]   
        elif index > num_bind_joints-5 and index < num_bind_joints-1:
            
            zero_based_index = index-(num_bind_joints-4)
            reverse_index = (num_bind_joints-2)-index
            
            # blend the jnt positions            
            blend_col = ctrl_joint_position_blend(  ctrl=end_ctrl,
                                                    ctrl_local_position=(linear_length_inc*((-reverse_index-1)),0,0),
                                                    point_on_crv_info=point_on_crv_info,
                                                    attr_name=blender_attr_name_list[reverse_index])
            blend_col.output >> jnt.translate
                        
        
        else:
            point_on_crv_info.position >> jnt.translate
        
        
        # orient constrain the first jnt to start ctrl
        if index == 0:
            pm.orientConstraint(start_ctrl, joint_list[index])

        # orient constrain the last jnt to end ctrl        
        elif index == num_bind_joints-1:
            pm.orientConstraint(end_ctrl, joint_list[index])
   
        # aim constrain the joints in between to aim at next bind joint    
        else:
            pm.aimConstraint(   joint_list[index+1],
                                joint_list[index],
                                aimVector=(1,0,0),
                                upVector=(0,0,1),
                                worldUpObject=start_ctrl,
                                worldUpType='objectrotation',
                                worldUpVector=(0,0,1))
                                                                        
     
    # organize       
    pm.parent(joint_list, bind_jnt_grp)
    pm.parent(cable_mesh, geo_grp)
    
    # set attrs
    bind_jnt_grp.inheritsTransform.set(False)                 
    geo_grp.inheritsTransform.set(False)
    
    cable_mesh.overrideEnabled.set(1)
    cable_mesh.overrideDisplayType.set(2)
    
    pm.setAttr(bind_jnt_grp.v, 0, lock=True)

        
 
    
       
#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/cable_crv_7_cvs.mb', f=True)
pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/cable_crv_10_cvs.mb', f=True)
#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/cable_crv.mb', f=True)
#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/cable_crv_11_cvs.mb', f=True)
#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/cable_crv_leg.mb', f=True)


crv = pm.PyNode('curve1')
#cable_base_dict = cable_base_ik(crv=crv, num_joints=4, name='test', pv_dir=1)
#create_joints_on_curve(crv=crv, num_joints=4, up_axis=2, parent_joints=True, show_lra=True, name='joint')

add_cable_bind_joints(crv=crv, name='cable_rig_name', num_ik_joints=4, num_bind_joints=20, pv_dir=1)
#cable_base_dict = cable_base_ik(crv=crv, num_joints=4, name='cable_rig_name',  pv_dir=1)

#def add_cable_bind_joints(crv, name, num_joints, show_lra=True, pv_dir=1):
    
'''
pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/crane_test.mb', f=True)

crv_list = [pm.PyNode('curve{0}'.format(n+1)) for n in range(4)]
for crv in crv_list:
    add_cable_bind_joints(crv=crv, name='cable_rig_name', num_joints=16, show_lra=False, pv_dir=1)
'''