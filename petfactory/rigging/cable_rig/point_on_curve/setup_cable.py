import pymel.core as pm
import maya.cmds as cmds
import pprint
import petfactory.rigging.nhair.nhair_dynamics as nhair_dynamics
import petfactory.modelling.mesh.extrude_profile as pet_extrude
reload(pet_extrude)

def add_curve_joints(crv, num_joints=10, name='name', cable_radius=.2, cable_axis_divisions=12, existing_hairsystem=None):
    
    cable_rig_main_grp = pm.group(em=True, name='cable_rig_main_grp')
    cluster_main_grp = pm.group(em=True, parent=cable_rig_main_grp, name='cluster_main_grp')
    crv_grp = pm.group(em=True, parent=cable_rig_main_grp, name='crv_grp')
    jnt_grp = pm.group(em=True, parent=cable_rig_main_grp, name='jnt_grp') 
    
    ret_dict = {}
    
    joint_list = []
    motionpath_list = []
    
    ret_dict['joint_list'] = joint_list

    crv_shape = crv.getShape()
    result_crv = crv.duplicate(name='result_crv')[0]
    result_crv_shape = result_crv.getShape()
    crv_shape.worldSpace[0] >> result_crv_shape.create
    
    pm.parent(crv, crv_grp)
    pm.parent(result_crv, crv_grp)
   
   
    # strat and end ctrl
    start_ctrl = pm.circle(name='start_ctrl', normal=(1,0,0))[0]
    pm.addAttr(start_ctrl, longName='dynamic_blendshape', minValue=0.0, maxValue=1.0, defaultValue=0.0, keyable=True)
    
    end_ctrl = pm.circle(name='end_ctrl', normal=(1,0,0))[0]
    
    pm.parent(end_ctrl, cable_rig_main_grp)
    pm.parent(start_ctrl, cable_rig_main_grp)
    

    # twist nodes    
    start_vec_prod = pm.createNode('vectorProduct', name='start_vector_prod')
    start_vec_prod.operation.set(3)
    start_vec_prod.input1.set(0,0,1)
    start_vec_prod.normalizeOutput.set(True)
    start_ctrl.worldMatrix[0] >> start_vec_prod.matrix
    
    
    end_vec_prod = pm.createNode('vectorProduct', name='end_vector_prod')
    end_vec_prod.operation.set(3)
    end_vec_prod.input1.set(0,0,1)
    end_vec_prod.normalizeOutput.set(True)
    end_ctrl.worldMatrix[0] >> end_vec_prod.matrix


    joint_list = [ pm.createNode('joint', name='mp_joint_{0}'.format(index), ss=True) for index in range(num_joints)]
    
    u_inc = 1.0/(num_joints-1)
    
    for index, jnt in enumerate(joint_list):
    
        #pm.toggle(jnt, localAxis=True)

        point_on_crv_info = pm.createNode('pointOnCurveInfo', name='point_on_crv_{0}'.format(index))
        point_on_crv_info.turnOnPercentage.set(True)
        result_crv_shape.worldSpace >> point_on_crv_info.inputCurve
        point_on_crv_info.parameter.set(u_inc*index)
        point_on_crv_info.position >> jnt.translate

        if index is 0:
            temp_const_start = pm.aimConstraint(joint_list[index+1], joint_list[index], aimVector=(1,0,0), upVector=(0,0,1), worldUpType='vector', worldUpVector=(start_vec_prod.output.get()))
            
            
        elif index is num_joints-1:
            temp_const_end = pm.aimConstraint(joint_list[index-1], joint_list[index], aimVector=(-1,0,0), upVector=(0,0,1), worldUpType='vector', worldUpVector=(start_vec_prod.output.get()))
                    
        else:
            
            blend_colors = pm.createNode('blendColors', name='test')
            blend_colors.blender.set(u_inc*index)
            start_vec_prod.output  >> blend_colors.color2
            end_vec_prod.output  >> blend_colors.color1
            
            
            aim_const = pm.aimConstraint(joint_list[index+1], joint_list[index], aimVector=(1,0,0), upVector=(0,0,1), worldUpType='vector', worldUpVector=(0,0,1))
            
            blend_colors.output >> aim_const.worldUpVector

    
    pm.delete(temp_const_start, temp_const_end)
    
    
    num_cvs = crv_shape.numCVs()

    cluster_grp_list = []
    for i in range(num_cvs-2):
        
        if i is 0:
            cv = '0:1'
            
        elif i is num_cvs-3:
            cv = '{0}:{1}'.format(num_cvs-2, num_cvs-1)
            
        else:
            cv = i+1
        
        #print(cv) 
        clust, clust_handle = pm.cluster('{0}.cv[{1}]'.format(crv.longName(), cv), relative=False, name='{0}_{1}_cluster_'.format(name, i))
        cluster_grp = pm.group(em=True, name='{0}_{1}_cluster_grp'.format(name, i))
        cluster_grp_list.append(cluster_grp)
        pm.parent(clust_handle, cluster_grp)
        pm.parent(cluster_grp, cluster_main_grp)





  
    start_ctrl.setMatrix(joint_list[0].getMatrix())
    end_ctrl.setMatrix(joint_list[-1].getMatrix())
    
    pm.orientConstraint(start_ctrl, joint_list[0], mo=True)
    pm.orientConstraint(end_ctrl, joint_list[-1], mo=True)
    
    
    pm.parent(joint_list, jnt_grp)
      
      
      
        
    # make the curves dynamic    
    nhair_dict_list = nhair_dynamics.make_curve_dynamic(crv)
    
    output_curve = nhair_dict_list.get('output_curve')
    follicle = nhair_dict_list.get('follicle')
    nucleus = nhair_dict_list.get('nucleus')
    hairsystem = nhair_dict_list.get('hairsystem')
    
    ret_dict['output_curve'] = output_curve
    ret_dict['follicle'] = follicle
    ret_dict['hairsystem'] = hairsystem
    
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
        ret_dict['nucleus'] = nucleus
        
        
    
    blendshape = pm.blendShape(output_curve, result_crv, origin='world')[0]
    
    start_ctrl.dynamic_blendshape >> blendshape.weight[0] 
    
    
    
    #mid_clust_grp_constraint = pm.parentConstraint(cluster_grp_list[0], cluster_grp_list[-1], cluster_grp_list[2])
    mid_clust_grp_constraint = pm.pointConstraint(cluster_grp_list[0], cluster_grp_list[-1], cluster_grp_list[2])
    
  
    #start_clust_grp_constraint = pm.parentConstraint(cluster_grp_list[0], cluster_grp_list[-1], cluster_grp_list[1])
    start_clust_grp_constraint = pm.pointConstraint(cluster_grp_list[0], cluster_grp_list[-1], cluster_grp_list[1])
    
    # get the weight list
    #start_weight_list = pm.parentConstraint(start_clust_grp_constraint, q=True, weightAliasList=True)
    start_weight_list = pm.pointConstraint(start_clust_grp_constraint, q=True, weightAliasList=True)
    start_weight_list[0].set(.75)
    start_weight_list[1].set(.25)
    
    #end_clust_grp_constraint = pm.parentConstraint(cluster_grp_list[0], cluster_grp_list[-1], cluster_grp_list[3])
    end_clust_grp_constraint = pm.pointConstraint(cluster_grp_list[0], cluster_grp_list[-1], cluster_grp_list[3])
    # get the weight list
    #end_weight_list = pm.parentConstraint(end_clust_grp_constraint, q=True, weightAliasList=True)
    end_weight_list = pm.pointConstraint(end_clust_grp_constraint, q=True, weightAliasList=True)
    end_weight_list[0].set(.25)
    end_weight_list[1].set(.75)
    
    
    
    # parent const to ctrl
    
    pm.parentConstraint(start_ctrl, cluster_grp_list[0], mo=True)
    pm.parentConstraint(end_ctrl, cluster_grp_list[-1], mo=True)

    # create mesh
    profile_pos = pet_extrude.create_profile_points(radius=cable_radius, axis_divisions=cable_axis_divisions, axis=0)
    
    extrude_pos_list = []
    for jnt in joint_list:
        
        tm = pm.datatypes.TransformationMatrix(jnt.getMatrix())
        pos = tm.getTranslation(space='world')
        extrude_pos_list.append( [p.rotateBy(tm)+pos for p in profile_pos] )

    mesh_dependnode = pet_extrude.mesh_from_pos_list(pos_list=extrude_pos_list, name='cable_mesh')
    cable_mesh = pm.PyNode('|{0}'.format(mesh_dependnode.name()))

    pm.parent(cable_mesh, cable_rig_main_grp)
    
    pm.skinCluster(joint_list, cable_mesh, tsb=True)

    
    return ret_dict
        

#pm.openFile('/Users/johan/Documents/projects/bot_pustervik/scenes/cable_crv.mb ', force=True)

#crv_1 = pm.PyNode('curve1')
#crv_2 = pm.PyNode('curve2')

#cable_dict_1 = add_curve_joints(crv=crv_1, cable_radius=.3, cable_axis_divisions=12)
#hairsystem_1 = cable_dict_1.get('hairsystem')

#cable_dict_2 = add_curve_joints(crv=crv_2, cable_radius=.3, cable_axis_divisions=12, existing_hairsystem=hairsystem_1)


#sel_list = pm.ls(sl=True)

crv_name_list = ['cable_rig_front_right', 'cable_rig_front_left']

for index, crv_name in enumerate(crv_name_list):
    

    crv = pm.PyNode(crv_name)
    
    if index is 0:
        
        cable_dict_1 = add_curve_joints(crv=crv, cable_radius=.3, cable_axis_divisions=12)
        hairsystem_1 = cable_dict_1.get('hairsystem')
    
    else:
        cable_dict_2 = add_curve_joints(crv=crv, cable_radius=.3, cable_axis_divisions=12, existing_hairsystem=hairsystem_1)

