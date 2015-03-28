import pymel.core as pm
import maya.mel as mel

from bisect import bisect_left, bisect_right
import petfactory.util.vector as pet_vector
reload(pet_vector)

import petfactory.rigging.ctrl.ctrl as pet_ctrl
import petfactory.modelling.mesh.extrude_profile as pet_extrude
import petfactory.rigging.nhair.nhair_dynamics as nhair_dynamics

import petfactory.rigging.ik_setup.stretchy_ik as stretchy_ik
reload(stretchy_ik)

import petfactory.rigging.skinning.curve_skinweight as curve_skinweight
reload(curve_skinweight)


'''
TODO

> set wigths of the nhair blendshape

'''
  
def validate_cv_num(num_joints, cv_num):
    
    def find_lt(a, x):
        'Find rightmost value less than x, if x is less than first val in a return a[0]'
        i = bisect_left(a, x)
        if i:
            return a[i-1]
        return a[0]



    def find_gt(a, x):
        'Find leftmost value greater than x, if x is greater than last val in a return a[-1]'
        i = bisect_right(a, x)
        if i != len(a):
            return a[i]
        return a[-1]
        
    
    valid_cv_num = [num_joints+(num_joints-1)*n for n in range(1, 30)]    
    
    lt = find_lt(valid_cv_num, cv_num)
    gt = find_gt(valid_cv_num, cv_num)
    
    pm.warning("Invalid number of cv's. Current cv num is {0}. Remove {1} cv(s) or add {2} cv(s)".format(cv_num, cv_num-lt, gt-cv_num))
    
    
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
    

def cable_base_ik(crv, num_joints, name='curve_rig', up_axis=2, existing_hairsystem=None):
        
    crv_shape = crv.getShape()
    num_cvs = crv_shape.numCVs()

    cvs_per_bone = float(num_cvs - num_joints) / (num_joints-1)
    min_cv_count = num_joints + (num_joints-1)
        
    # check if the number of cvs are valid
    if num_cvs >= min_cv_count and cvs_per_bone % 1 == 0:
        print('Start rigging the cable...')
    
    else:
        #pm.warning('The number of cvs must be at least {0} and follow pattern num_jnt+(num_jnt-1)*n where n is positive integer'.format(min_cv_count))
        validate_cv_num(num_joints, num_cvs)
        return None
        
        
    # duplicate the crv, freeze transform, keep the position
    crv = pm.duplicate(crv, n='{0}_cubic_crv'.format(name))[0]
    pm.makeIdentity(crv, apply=True)
    crv_shape = crv.getShape()
    crv_length = pm.arclen(crv)
    
    # display the cvs
    #pm.toggle(crv_shape, cv=True, hull=True)
          
    #num_linear_crv_div = (num_cvs - 3) / 2    
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
    no_inherit_trans_grp = pm.group(em=True, parent=hidden_grp, n='{0}_no_inherit_trans_grp'.format(name))
    no_inherit_trans_grp.inheritsTransform.set(0)

    # create the ik joints
    ik_jnt_list = create_joints_on_curve(crv=crv, num_joints=num_joints, up_axis=2, parent_joints=True, show_lra=True, name='{0}_base_ik'.format(name))
    
    # calculate the start and end t matrix
    start_matrix = matrix_from_u(crv=crv, start_u=0, end_u=.05, pos_u=0, up_vec=up_vec)
    end_matrix = matrix_from_u(crv=crv, start_u=max_u-.05, end_u=max_u, pos_u=max_u, up_vec=up_vec)
    
    # create start and end ctrl
    ctrl_start = pet_ctrl.CreateCtrl.create_circle_arrow(name='{0}_start_ctrl'.format(name), size=1)
    ctrl_start.setMatrix(start_matrix)
    
    ctrl_end = pet_ctrl.CreateCtrl.create_circle_arrow(name='{0}_end_ctrl'.format(name), size=1)
    ctrl_end.setMatrix(end_matrix)
   
    # build the linear curve 
    jnt_pos_list = [ jnt.getTranslation(space='world') for jnt in ik_jnt_list ]
    pos_list = pet_vector.interpolate_positions(pos_list=jnt_pos_list, num_divisions=int(cvs_per_bone))
    
    # create an stretchy ik spring rig
    stretchy_ik_dict = stretchy_ik.create_ik_spring(    ik_jnt_list=ik_jnt_list,
                                                        start_ctrl=ctrl_start,
                                                        end_ctrl=ctrl_end,
                                                        name=name,
                                                        move_ctrl=False)
    
    # get some info from the strechy spring rig
    stretch_condition = stretchy_ik_dict['stretch_condition']
    stretch_distance_shape = stretchy_ik_dict['distance_shape']
    stretch_ik_jnt_grp = stretchy_ik_dict['ik_jnt_grp']
    start_ctrl_hidden_grp = stretchy_ik_dict['start_ctrl_hidden_grp']
    end_ctrl_hidden_grp = stretchy_ik_dict['end_ctrl_hidden_grp']
    jont_chain_length = stretchy_ik_dict['total_jnt_length']
    
    
    # add the linear crv
    stretchy_lin_crv_dict = stretchy_ik.add_linear_stretch_crv( ik_jnt_list=ik_jnt_list,
                                                                spring_ik_dict=stretchy_ik_dict,
                                                                num_div=int(cvs_per_bone),
                                                                name=name)
       
    
    # get info from the linear crv
    crv_linear = stretchy_lin_crv_dict['crv_linear']
    
    
    pm.addAttr(ctrl_start, longName='show_ik_joints', at="enum", en="off:on", keyable=True)

    
    ctrl_start.show_ik_joints >> stretch_ik_jnt_grp.v
    
    stretch_ik_jnt_grp.overrideEnabled.set(1)
    stretch_ik_jnt_grp.overrideDisplayType.set(2)
    
    # bind the skin
    skin_cluster_cubic = pm.skinCluster(ik_jnt_list[0], crv)


    
    # create the blendshape
    blendshape_linear = pm.blendShape(crv_linear, crv, origin='local')[0]
    
    linear_blendshape_RMV = pm.createNode('remapValue', name='linear_blendshape_RMV')
    
    
    stretch_distance_shape.distance >> linear_blendshape_RMV.inputValue
    
    # set the min to 90 percent of the crv length, max to crv length    
    pm.addAttr(ctrl_start, ln='blendshape_min', at='double', k=False, defaultValue=jont_chain_length*.8)
    pm.addAttr(ctrl_start, ln='blendshape_max', at='double', k=False, defaultValue=crv_length*.9)
    
    ctrl_start.blendshape_min >> linear_blendshape_RMV.inputMin
    ctrl_start.blendshape_max >> linear_blendshape_RMV.inputMax
    
    # set the first value point to use a spline interpolation
    linear_blendshape_RMV.value[0].value_Interp.set(3)
    
    # set the blendshape weight to 1 (weighted to the linear crv) when we bind the crv
    # this will ensure that we get the correct deformation when the crv is stretched
    # if we do not do this the cvs will be slighlty off (maya bug?)
    # blendshape_linear.linear_curve_bs.set(1.0)
    blendshape_linear.weight[0].set(1.0)
       
    # connect the remap out value to control the blendshape
    #linear_blendshape_RMV.outValue >> blendshape_linear.linear_curve_bs
    linear_blendshape_RMV.outValue >> blendshape_linear.weight[0]


    # organize
    pm.parent(ctrl_start, ctrl_end, ctrl_grp)
    pm.parent(crv_linear, no_inherit_trans_grp)
    pm.parent(crv, bind_geo_grp)
        
    # uncheck inherit transform on cubic crv
    crv.inheritsTransform.set(0)
    
    # hide grp
    pm.setAttr(hidden_grp.v, 0, lock=True)
    
    crv_shape.overrideEnabled.set(1)
    crv_shape.overrideDisplayType.set(2)
    
    
    bind_geo_grp.overrideEnabled.set(1)
    bind_geo_grp.overrideDisplayType.set(2)
    
    # make the curves dynamic    
    nhair_dict = nhair_dynamics.make_curve_dynamic(crv, delete_out_curve_parent=True)

    output_curve = nhair_dict.get('output_curve')
    output_curve.rename('{0}_output_curve'.format(name))
    hairsystem = nhair_dict.get('hairsystem')
    follicle = nhair_dict.get('follicle')
    follicle.rename('{0}_follicle'.format(name))
    nucleus = nhair_dict.get('nucleus')
    
       
    # if we want to use an existing hair system
    if existing_hairsystem is not None:
        
        print('Delete current hairsystem, use {0}'.format(existing_hairsystem))
        
        num_connection = len(pm.listConnections('{0}.inputHair'.format(existing_hairsystem)))
        
        follicle.outHair >> existing_hairsystem.inputHair[num_connection]
        existing_hairsystem.outputHair[num_connection] >> follicle.currentPosition
        
        pm.delete(hairsystem)
        
        hairsystem = existing_hairsystem
        
    else:         
        hairsystem.startCurveAttract.set(0.1)
    
     
    # create a duplicate of the orig crv
    result_crv_shape = pm.createNode('nurbsCurve', n='{0}_result_crvShape'.format(name))
    result_crv = result_crv_shape.getParent()
    result_crv.rename('{0}_result_crv'.format(name))

    crv_shape.worldSpace[0] >> result_crv_shape.create
    nhair_blendshape = pm.blendShape(output_curve, result_crv, origin='local')[0]
    # , n='{0}_nhair_blendshape'.format(name)
        
    # add attr to control the nahir blend shape
    pm.addAttr(ctrl_start, longName='use_nhair_sim', keyable=True, min=0, max=1, defaultValue=0)
    ctrl_start.use_nhair_sim >> nhair_blendshape.weight[0]
    

    # set the nhair blendshape weight of the two first and last cvs to 0
    nhair_blendshape.inputTarget[0].baseWeights[0].set(0)
    nhair_blendshape.inputTarget[0].baseWeights[1].set(0)
    
    nhair_blendshape.inputTarget[0].baseWeights[num_cvs-1].set(0)
    nhair_blendshape.inputTarget[0].baseWeights[num_cvs-2].set(0)
    
    
    pm.parent(result_crv, output_curve, no_inherit_trans_grp)
    
    ret_dict = {}
    ret_dict['start_ctrl'] = ctrl_start
    ret_dict['end_ctrl'] = ctrl_end
    ret_dict['curve_cubic'] = result_crv
    ret_dict['curve_linear'] = crv_linear
    ret_dict['remap_value'] = linear_blendshape_RMV
    ret_dict['main_grp'] = main_grp
    ret_dict['no_inherit_trans_grp'] = no_inherit_trans_grp
    ret_dict['hairsystem'] = hairsystem
    ret_dict['follicle'] = follicle
    
    return ret_dict

    
  
def matrix_from_u(crv, start_u, end_u, pos_u, up_vec):
    
    crv_shape = crv.getShape()
    
    start_p = crv_shape.getPointAtParam(start_u, space='world')
    end_p = crv_shape.getPointAtParam(end_u, space='world')
    pos_p = crv_shape.getPointAtParam(pos_u, space='world')
    
    aim_vec = end_p - start_p
    
    tm = pet_vector.remap_aim_up(aim_vec, up_vec, aim_axis=0, up_axis=2, invert_aim=False, invert_up=False, pos=pos_p)
    return tm
    
    
def mesh_from_start_end(start_joint, end_joint, length_divisions=10, cable_radius=.5, cable_axis_divisions=12, name='mesh'):

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
    
    
    # add some pos to the extrude pos list to create the caps, somewhat hacky...
    # add start cap     
    se_0 = [n*.7 for n in extrude_pos_list[0]]
    se_1 = [n*.9 for n in extrude_pos_list[0]]
    se_3 = [(n.x+(length_inc*.15), n.y, n.z) for n in extrude_pos_list[0]] 
    
    # add end cap     
    ee_0 = [(n.x-(length_inc*.15), n.y, n.z) for n in extrude_pos_list[-1]]
    ee_1 = [(n.x*.9+length_inc*(length_divisions-1), n.y*.9, n.z*.9) for n in extrude_pos_list[0]]
    ee_2 = [(n.x*.7+length_inc*(length_divisions-1), n.y*.7, n.z*.7) for n in extrude_pos_list[0]]
    
    # add the cap positions
    extrude_pos_list.insert(0, se_0)
    extrude_pos_list.insert(1, se_1)
    extrude_pos_list.insert(3, se_3)
    
    extrude_pos_list.insert(-1, ee_0)
    extrude_pos_list.append(ee_1)
    extrude_pos_list.append(ee_2)
    
    
        
    pm_mesh = pet_extrude.mesh_from_pos_list(pos_list=extrude_pos_list, name=name, as_pm_mesh=True) 

    return pm_mesh
    
        
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
    
def add_cable_bind_joints(crv, name, num_ik_joints, num_bind_joints, cable_radius, cable_axis_divisions, existing_hairsystem=None, create_mesh_copy=False, show_lra=False):
    
    ret_dict = {}
    
    blender_attr_name_list = ['blendJoint1', 'blendJoint2', 'blendJoint3']
    blender_value_list = [.7, .4, .1]
        
    cable_base_dict = cable_base_ik(crv=crv, num_joints=num_ik_joints, name=name, existing_hairsystem=existing_hairsystem)
    
    if cable_base_dict is None:
        return None
        
        
    cubic_crv = cable_base_dict['curve_cubic']
    linear_crv = cable_base_dict['curve_linear']
    start_ctrl = cable_base_dict['start_ctrl']
    end_ctrl = cable_base_dict['end_ctrl']
    linear_blendshape_RMV = cable_base_dict['remap_value']
    main_grp = cable_base_dict['main_grp']
    no_inherit_trans_grp = cable_base_dict['no_inherit_trans_grp']
    
    ret_dict['hairsystem'] = cable_base_dict['hairsystem']
    ret_dict['follicle'] = cable_base_dict['follicle']
    ret_dict['start_ctrl'] = cable_base_dict['start_ctrl']
    ret_dict['end_ctrl'] = cable_base_dict['end_ctrl']
    
    
    for index, attr_name in enumerate(blender_attr_name_list):
        
        pm.addAttr(start_ctrl, longName=attr_name, keyable=True, min=0, max=1, defaultValue=blender_value_list[index])
        pm.addAttr(end_ctrl, longName=attr_name, keyable=True, min=0, max=1, defaultValue=blender_value_list[index])

        
    bind_jnt_grp = pm.group(em=True, parent=no_inherit_trans_grp, n='{0}_bind_jnt_grp'.format(name))
    geo_grp = pm.group(em=True, parent=main_grp, n='{0}_geo_grp'.format(name))
        
    linear_crv_shape = linear_crv.getShape()
    linear_crv_min_u, linear_crv_max_u = linear_crv_shape.getKnotDomain()
    linear_curve_length = linear_crv_shape.length()
    
    cubic_crv_shape = cubic_crv.getShape()
    cubic_crv_min_u, cubic_crv_max_u = cubic_crv_shape.getKnotDomain()
    cubic_curve_length = cubic_crv_shape.length()
    
    cubic_length_inc = cubic_curve_length / (num_bind_joints-1)
    linear_length_inc = linear_curve_length / (num_bind_joints-1)
    
    
    # build the cable joints
    joint_list = create_joints_on_axis(num_joints=num_bind_joints, show_lra=show_lra, spacing=cubic_length_inc)
        
    # create the mesh
    cable_mesh = mesh_from_start_end(start_joint=joint_list[0], end_joint=joint_list[-1], length_divisions=(num_bind_joints*2)-1, cable_radius=cable_radius, cable_axis_divisions=cable_axis_divisions, name='{0}_mesh'.format(name))
    ret_dict['mesh'] = cable_mesh
    
    if create_mesh_copy:
        mesh_copy = pm.duplicate(cable_mesh, name='{0}_dup_mesh'.format(name))
    
    #pm.skinCluster(joint_list, cable_mesh, toSelectedBones=True, ignoreHierarchy=True, skinMethod=2, maximumInfluences=3)
    pm.skinCluster(joint_list, cable_mesh, bindMethod=0)
    
    # organize
    pm.parent(cable_mesh, geo_grp)            
    geo_grp.inheritsTransform.set(False)
    cable_mesh.overrideEnabled.set(1)
    cable_mesh.overrideDisplayType.set(2)
    

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
    
    return ret_dict
    




def setup_crv_list( crv_list,
                    rig_name,
                    name_start_index,
                    num_ik_joints,
                    num_bind_joints,
                    cable_radius,
                    cable_axis_divisions,
                    mesh_set = None,
                    follicle_set = None,
                    start_ctrl_set = None,
                    end_ctrl_set = None,
                    use_existing_hairsystem = False,
                    share_hairsystem = True,
                    existing_hairsystem = None
                    ):
    
    # deselect while creating the sets    
    pm.select(deselect=True)
    
    if mesh_set is None:                
        mesh_set = pm.sets(name='mesh_set')
      
    if follicle_set is None:  
        follicle_set = pm.sets(name='follicle_set')
    
    if start_ctrl_set is None:
        start_ctrl_set = pm.sets(name='start_ctrl_set')
        
    if end_ctrl_set is None:
        end_ctrl_set = pm.sets(name='end_ctrl_set')
        
    
    for index, crv in enumerate(crv_list):
        
        if use_existing_hairsystem:
            
            if index is 0:
                cable_dict = add_cable_bind_joints(crv=crv, name='{0}_{1}'.format(rig_name, index+name_start_index), num_ik_joints=num_ik_joints, num_bind_joints=num_bind_joints, cable_radius=cable_radius, cable_axis_divisions=cable_axis_divisions, existing_hairsystem=existing_hairsystem, create_mesh_copy=True)
                
            else:
                cable_dict = add_cable_bind_joints(crv=crv, name='{0}_{1}'.format(rig_name, index+name_start_index), num_ik_joints=num_ik_joints, num_bind_joints=num_bind_joints, cable_radius=cable_radius, cable_axis_divisions=cable_axis_divisions, existing_hairsystem=existing_hairsystem)
            
            
            
        # do not use existing hs
        else:
            
            # create a new hs at index 0, share this hs
            if share_hairsystem:
                
                if index is 0:
                    cable_dict = add_cable_bind_joints(crv=crv, name='{0}_{1}'.format(rig_name, index+name_start_index), num_ik_joints=num_ik_joints, num_bind_joints=num_bind_joints, cable_radius=cable_radius, cable_axis_divisions=cable_axis_divisions, create_mesh_copy=True)
                    existing_hairsystem = cable_dict.get('hairsystem')
                    
                else:
                    cable_dict = add_cable_bind_joints(crv=crv, name='{0}_{1}'.format(rig_name, index+name_start_index), num_ik_joints=num_ik_joints, num_bind_joints=num_bind_joints, cable_radius=cable_radius, cable_axis_divisions=cable_axis_divisions, existing_hairsystem=existing_hairsystem)
                    
                    
            # create a new hs for each rig
            else:
                if index is 0:
                    cable_dict = add_cable_bind_joints(crv=crv, name='{0}_{1}'.format(rig_name, index+name_start_index), num_ik_joints=num_ik_joints, num_bind_joints=num_bind_joints, cable_radius=cable_radius, cable_axis_divisions=cable_axis_divisions, create_mesh_copy=True)
                
                else:
                    cable_dict = add_cable_bind_joints(crv=crv, name='{0}_{1}'.format(rig_name, index+name_start_index), num_ik_joints=num_ik_joints, num_bind_joints=num_bind_joints, cable_radius=cable_radius, cable_axis_divisions=cable_axis_divisions)
                    

        # add to sets
        
        if cable_dict is None:
            return None
            
        mesh_set.add(cable_dict['mesh'])
        follicle_set.add(cable_dict['follicle'])
        start_ctrl_set.add(cable_dict['start_ctrl'])
        end_ctrl_set.add(cable_dict['end_ctrl'])
                            


#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/cable_crv_10_cvs_tripple_nhair.mb', f=True)
pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/cable_crv_10_cvs_single_nhair.mb', f=True)


crv_1 = pm.PyNode('curve1')
#crv_2 = pm.PyNode('curve2')
#crv_3 = pm.PyNode('curve3')
#crv_list = [crv_1, crv_2, crv_3]
crv_list = [crv_1]


rig_name = 'cable_rig_name'
name_start_index = 0
num_ik_joints = 4
num_bind_joints = 20
cable_radius = .5
cable_axis_divisions = 12


mesh_set = None
follicle_set = None
start_ctrl_set = None
end_ctrl_set = None

use_existing_hairsystem = True
share_hairsystem = True
#existing_hairsystem = None
existing_hairsystem = pm.PyNode('hairSystem1')

setup_crv_list( crv_list,
                rig_name,
                name_start_index,
                num_ik_joints,
                num_bind_joints,
                cable_radius,
                cable_axis_divisions,
                mesh_set,
                follicle_set,
                start_ctrl_set,
                end_ctrl_set,
                use_existing_hairsystem,
                share_hairsystem,
                existing_hairsystem)


#cable_base_ik(crv, num_joints, name='curve_rig', up_axis=2, existing_hairsystem=None):
#cable_base_ik(crv=crv_1, num_joints=num_ik_joints, name='curve_rig', up_axis=2, existing_hairsystem=existing_hairsystem)

pm.delete(crv_list)   
