import pymel.core as pm
import petfactory.util.vector as pet_vector

'''
TODO

add pole vector

'''
def create_joints_on_curve(crv, num_joints, up_axis, parent_joints=True, show_lra=True, name='joint'):
    
    crv_shape = crv.getShape()
    length = crv_shape.length()
    length_inc = length / (num_joints-1)
    
    crv_matrix = crv.getMatrix(worldSpace=True)
        
    up_vec = pm.datatypes.Vector(crv_matrix[up_axis][0], crv_matrix[up_axis][1], crv_matrix[up_axis][2])
    up_vec.normalize()
    
    
    jnt_list = []
    for index in range(num_joints):
        
        u = crv_shape.findParamFromLength(length_inc*index)
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
                
                
    parent_joint_list(jnt_list)
    
    return jnt_list
            
            
def parent_joint_list(joint_list):         
    for index, jnt in enumerate(joint_list):
        if index > 0:
            pm.parent(joint_list[index], joint_list[index-1])
    pm.select(deselect=True)
    

def cable_base_ik(crv, name='curve_rig'):
    
    crv = pm.duplicate(crv, n='{0}_cubic_crv'.format(name))[0]
    # freeze transform, keep the position
    pm.makeIdentity(crv, apply=True)
    
    crv_shape = crv.getShape()
    num_cvs = crv_shape.numCVs()
    num_linear_crv_div = (num_cvs - 3) / 2
    
    
    if num_cvs < 5 or num_cvs % 2 == 0:
        pm.warning('Please use a curve that has an uneven number of cvs that is greater than 4')
        return
        
    
    main_grp = pm.group(em=True, n='{0}_main_grp'.format(name))
    ctrl_grp = pm.group(em=True, parent=main_grp, n='{0}_ctrl_grp'.format(name))
    bind_geo_grp = pm.group(em=True, parent=main_grp, n='{0}_bind_geo_grp'.format(name))
    hidden_grp = pm.group(em=True, parent=main_grp, n='{0}_hidden_grp'.format(name))
    #crv = pm.rebuildCurve(crv, keepRange=False, keepControlPoints=True, ch=False, rebuildType=0, replaceOriginal=False, name='new_crv')[0]
    
    # create the ik joints
    ik_jnt_list = create_joints_on_curve(crv=crv, num_joints=3, up_axis=2, parent_joints=True, show_lra=True, name=name)
    
    ctrl_start = pm.circle(n='{0}_start_ctrl'.format(name))[0]
    ctrl_start.setMatrix(ik_jnt_list[0].getMatrix(worldSpace=True))
    
    ctrl_end = pm.circle(n='{0}_end_ctrl'.format(name))[0]
    ctrl_end.setMatrix(ik_jnt_list[-1].getMatrix(worldSpace=True))
    # calculate the cv pos of the lin crv 
    pos_list = get_pos_on_line(start=ik_jnt_list[0].getTranslation(space='world'), end=ik_jnt_list[1].getTranslation(space='world'), num_divisions=num_linear_crv_div, include_start=True, include_end=True)
    pos_list.extend(get_pos_on_line(start=ik_jnt_list[1].getTranslation(space='world'), end=ik_jnt_list[2].getTranslation(space='world'), num_divisions=num_linear_crv_div, include_start=False, include_end=True))
    
    # build the linear blendshape crv
    #temp_crv_linear = pm.curve(d=3, p=pos_list)
    #crv_linear = pm.rebuildCurve(temp_crv_linear, keepRange=False, keepControlPoints=True, ch=False, rebuildType=0, replaceOriginal=False, n='linear_curve_bs')[0]
    crv_linear = pm.curve(d=3, p=pos_list, n='{0}_linear_crv'.format(name))
    #crv_linear = pm.curve(d=3, p=pos_list, n='linear_curve_bs')
    
    
  
    # bind, add ik handle  
    ik_handle, ik_effector = pm.ikHandle(sj=ik_jnt_list[0], ee=ik_jnt_list[-1], n='{0}_ikh'.format(name), solver='ikRPsolver')
  
    
    dist = pm.distanceDimension(sp=ik_jnt_list[0].getTranslation(space='world'), ep=ik_jnt_list[-1].getTranslation(space='world'))
    dist_transform = dist.getParent()
    dist_transform.rename('{0}_dist'.format(name))
    start_loc = pm.listConnections( '{0}.startPoint'.format(dist))[0]
    start_loc.rename('start_loc')
    end_loc = pm.listConnections( '{0}.endPoint'.format(dist))[0]
    end_loc.rename('end_loc')
    
    
    
    linear_blendshape_RMV = pm.createNode('remapValue', name='linear_blendshape_RMV')
    
    crv_length = pm.arclen(crv)
    jont_chain_length = ik_jnt_list[1].tx.get() + ik_jnt_list[-1].tx.get()
    
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
    
    jnt_cable_rig_stretch_CND.outColorR >> ik_jnt_list[0].scaleX
    jnt_cable_rig_stretch_CND.outColorR >> ik_jnt_list[1].scaleX
    
    
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
    pole_vector_target = pm.spaceLocator(n='polevector_target')
    pole_vector_target_grp = pm.group(em=True, n='polevector_target_grp')
    pm.parent(pole_vector_target, pole_vector_target_grp)
    pole_vector_target_grp.setMatrix(ik_jnt_list[0].getMatrix(worldSpace=True))
    pole_vector_target.tz.set(10)
    
    polevector_const = pm.poleVectorConstraint(pole_vector_target, ik_handle)
    ik_handle.twist.set(-90)
    
    # organize
    pm.parent(start_loc, ctrl_start)
    pm.parent(ik_handle, end_loc, ctrl_end)
    pm.parent(ik_jnt_list[0], ctrl_start)
    
    pm.parent(ctrl_start, ctrl_end, ctrl_grp)
    pm.parent(dist_transform, pole_vector_target_grp, crv_linear, hidden_grp)
    pm.parent(crv, bind_geo_grp)
    
    # uncheck inherit transform on cubic crv
    crv.inheritsTransform.set(0)
    
    # hide grp
    hidden_grp.visibility.set(0)

    
    
    
def get_pos_on_line(start, end, num_divisions, include_start=False, include_end=False):
    
    start_vec = pm.datatypes.Vector(start)
    end_vec = pm.datatypes.Vector(end)
    delta = end_vec - start_vec
       
    u_inc = 1.0 / (num_divisions+1)
    
    pos_list = []
    for n in range(num_divisions+2):
        
        if n is 0:
            if include_start:
                pos_list.append(start_vec)
            
        elif n is num_divisions+1:
            if include_end:
                pos_list.append(end_vec)
        else:
            pos_list.append(delta * (u_inc*n) + start_vec)
        
    return pos_list
        
        
   
#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/cable_crv_7_cvs.mb', f=True)
#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/cable_crv.mb', f=True)
#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/cable_crv_11_cvs.mb', f=True)
pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/cable_crv_leg.mb', f=True)

crv = pm.PyNode('curve1')

cable_base_ik(crv)

