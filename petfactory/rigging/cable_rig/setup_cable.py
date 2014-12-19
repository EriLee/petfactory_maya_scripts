import pymel.core as pm
import maya.cmds as cmds
import pprint
import petfactory.rigging.nhair.nhair_dynamics as nhair_dynamics
import petfactory.modelling.mesh.extrude_profile as pet_extrude
reload(pet_extrude)

def add_curve_joints(crv, num_joints=10, name='name', cable_radius=.2, cable_axis_divisions=12, front_axis=0, up_axis=1):
    
    ''' creates joints that are animated along the specified curve'''

    if front_axis < 0 or front_axis > 2 or up_axis < 0 or up_axis > 2:
        pm.warning('the front or the up axis must be in range 0-2')
        return
        
    if front_axis == up_axis:
        pm.warning('the front axis can not be the same as the up axis')
        return
        
    u_front_axis = ['x', 'y', 'z'][front_axis]
    u_up_axis = ['x', 'y', 'z'][up_axis]
    
    
    ret_dict = {}
    
    joint_list = []
    motionpath_list = []
    
    ret_dict['joint_list'] = joint_list
    ret_dict['motionpath_list'] = motionpath_list

    crv_shape = crv.getShape()
    result_crv = crv.duplicate(name='result_crv')[0]
    result_crv_shape = result_crv.getShape()
    crv_shape.worldSpace[0] >> result_crv_shape.create
    
    start_ctrl = pm.circle(name='start_ctrl', normal=(1,0,0))[0]
    
    u_inc = 1.0/(num_joints-1)

    joint_list = [ pm.createNode('joint', name='mp_joint_{0}'.format(index), ss=True) for index in range(num_joints)]
    
    for index, jnt in enumerate(joint_list):
    
        print(jnt)
        pm.toggle(jnt, localAxis=True)

        point_on_crv_info = pm.createNode('pointOnCurveInfo', name='point_on_crv_{0}'.format(index))
        point_on_crv_info.turnOnPercentage.set(True)
        result_crv_shape.worldSpace >> point_on_crv_info.inputCurve
        point_on_crv_info.parameter.set(u_inc*index)
        point_on_crv_info.position >> jnt.translate

        if index < num_joints-1:
            pm.aimConstraint(joint_list[index+1], joint_list[index], aimVector=(1,0,0), upVector=(0,0,1), worldUpType='objectrotation', worldUpObject=start_ctrl, worldUpVector=(0,0,1))
            
        else:
            pm.aimConstraint(joint_list[index-1], joint_list[index], aimVector=(-1,0,0), upVector=(0,0,1), worldUpType='objectrotation', worldUpObject=start_ctrl, worldUpVector=(0,0,1))
            
 
    
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

    
    #start_ctrl = pm.circle(name='start_ctrl', normal=(1,0,0))[0]
    pm.addAttr(start_ctrl, longName='dynamic_blendshape', minValue=0.0, maxValue=1.0, defaultValue=1.0, keyable=True)
    
    end_ctrl = pm.circle(name='end_ctrl', normal=(1,0,0))[0]
    
    start_ctrl.setMatrix(joint_list[0].getMatrix())
    end_ctrl.setMatrix(joint_list[-1].getMatrix())
    
    jnt_grp = pm.group(em=True, name='jnt_grp') 
    pm.parent(joint_list, jnt_grp)
      
      
      
        
    # make the curves dynamic    
    nhair_dict_list = nhair_dynamics.make_curve_dynamic(crv)
    
    output_curve = nhair_dict_list.get('output_curve')
    follicle = nhair_dict_list.get('follicle')
    nucleus = nhair_dict_list.get('nucleus')
    hairsystem = nhair_dict_list.get('hairsystem')
    
    hairsystem.startCurveAttract.set(0.005)
    nucleus.spaceScale.set(.1)
    
    blendshape = pm.blendShape(output_curve, result_crv, origin='world')[0]
    
    start_ctrl.dynamic_blendshape >> blendshape.weight[0] 
    
    
    
    mid_clust_grp_constraint = pm.parentConstraint(cluster_grp_list[0], cluster_grp_list[-1], cluster_grp_list[2])
    
  
    start_clust_grp_constraint = pm.parentConstraint(cluster_grp_list[0], cluster_grp_list[-1], cluster_grp_list[1])
    start_weight_list = pm.parentConstraint(start_clust_grp_constraint, q=True, weightAliasList=True)
    start_weight_list[0].set(.75)
    start_weight_list[1].set(.25)
    
    end_clust_grp_constraint = pm.parentConstraint(cluster_grp_list[0], cluster_grp_list[-1], cluster_grp_list[3])
    end_weight_list = pm.parentConstraint(end_clust_grp_constraint, q=True, weightAliasList=True)
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
        
    #pprint.pprint(extrude_pos_list)
    cable_mesh = pet_extrude.mesh_from_pos_list(pos_list=extrude_pos_list, name='cable_mesh')
    
    pm.skinCluster(joint_list, cable_mesh,tsb=True)

    
    return ret_dict
        

#pm.openFile('/Users/johan/Documents/projects/bot_pustervik/scenes/cable_crv.mb ', force=True)
#crv = pm.PyNode('curve1')

sel_list = pm.ls(sl=True)
if sel_list:
    add_curve_joints(crv=sel_list[0], cable_radius=.3, cable_axis_divisions=12)