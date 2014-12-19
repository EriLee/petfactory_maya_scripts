import pymel.core as pm
import petfactory.rigging.nhair.nhair_dynamics as nhair_dynamics

pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)

# one idea is to use a crv as a ref to get the length, and position of cv
# the map that out flat with an even spacing, create the crv rig, with joints etc
# create cable meash from duplicated geo, duplicate combine, merge, bind to the joints
# the move crv into position.

main_cable_grp = pm.group(em=True, name='main_cable_grp')
misc_grp = pm.group(em=True, name='misc_grp', parent=main_cable_grp)
hidden_grp = pm.group(em=True, name='hidden_grp', parent=misc_grp)
hidden_grp.visibility.set(False)

num_joints = 10
jnt_list = []

# the crv, should be 3 degree, with 5 cvs
crv = pm.curve(name='orig_crv', d=3, ep=[(-5, 0, 0), (0, 0, 0), (5, 0, 0)])

result_crv = pm.duplicate(crv, name='result_crv')[0]

crv.worldSpace >> result_crv.create

# create and position the start and end ctrl
start_ctrl = pm.circle(normal=(1,0,0), name='start')[0]
end_ctrl = pm.circle(normal=(1,0,0), name='end')[0]

# add attr to start ctrl
pm.addAttr(start_ctrl, longName='stretchScale', defaultValue=1.0, keyable=True)
pm.addAttr(start_ctrl, longName='Mode', at="enum", en="Static:Dynamic", keyable=True)


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
    pm.toggle(jnt, localAxis=True)
    
    # parent the jnt
    if index > 0:
        pm.parent(jnt, jnt_list[index-1])
    
    

start_ctrl.setMatrix(jnt_list[0].getMatrix(ws=True))
end_ctrl.setMatrix(jnt_list[-1].getMatrix(ws=True))


# create the ikSpline
iks_handle, effector = pm.ikHandle(solver='ikSplineSolver', curve=crv, parentCurve=False, createCurve=False, rootOnCurve=False, twistType='easeInOut', sj=jnt_list[0], ee=jnt_list[-1])

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


'''
# create a crv that will be used as a target for the nhair
# drive the nhair target crv with the orig crv, set the full weight (index, weight)
nhair_target_crv = pm.duplicate(crv, name='nhair_target_crv')[0]
pm.blendShape(crv, nhair_target_crv, origin='world', weight = (0,1))

# make the nhair_target_crv dynamic
nhair_dict = nhair_dynamics.make_curve_dynamic(nhair_target_crv)
output_crv = nhair_dict.get('output_curve')
follicle = nhair_dict.get('follicle')

# create a crv that will drive the ikspline, blend the orig crv, dynamic crv
# set the weight of index 0 to 1 weigth = (0,1)
result_spline_crv = pm.duplicate(crv, name='result_spline_crv')[0]
result_blendshape = pm.blendShape(crv, output_crv, result_spline_crv, origin='world', weight = (0,1))[0]

# setup the mode to switch between static and dynamic
reverse_mode = pm.createNode('reverse', name='reverse_mode')
start_ctrl.Mode >> reverse_mode.input.inputX
reverse_mode.outputX >> result_blendshape.weight[0]
start_ctrl.Mode >> result_blendshape.weight[1]


# create a crv info, to get the arclength
result_crv_info = pm.arclen(result_spline_crv, ch=True)

# setup the joint stretch, divide the crv length with the number of joints to
# to get a value of how much to scale each joint to reach the full crv length
# the output from the mult double linear will be fed into the scale x of the jnts
stretch_scale_mult = pm.createNode('multDoubleLinear', name='stretch_scale_mult')
arclen_mult = pm.createNode('multDoubleLinear', name='arclen_mult')

start_ctrl.stretchScale >> stretch_scale_mult.input1
stretch_scale_mult.input2.set(1.0/num_joints)

result_crv_info.arcLength >> arclen_mult.input1
stretch_scale_mult.output >> arclen_mult.input2


# get the max u value
crv_shape = crv.getShape()
num_cvs = crv_shape.numCVs()
min_u, max_u = crv_shape.getKnotDomain()
# get a u value increment from start to end
u_inc = max_u / (num_joints-1)
for index in range(num_joints):
    
    pos = crv_shape.getPointAtParam(u_inc * index, space='world')

    # create the joints
    jnt = pm.createNode('joint', name='jnt_{0}'.format(index), ss=True)
    jnt_list.append(jnt)
    jnt.translate.set(pos)
    pm.toggle(jnt, localAxis=True)
    
    # setup the joint stretch
    arclen_mult.output >> jnt.scaleX
    
    # parent the jnt
    if index > 0:
        pm.parent(jnt, jnt_list[index-1])
    

# position the ctrl
start_ctrl.setMatrix(jnt_list[0].getMatrix(ws=True))
end_ctrl.setMatrix(jnt_list[-1].getMatrix(ws=True))


# create the ikSpline
iks_handle, effector = pm.ikHandle(solver='ikSplineSolver', curve=result_spline_crv, parentCurve=False, createCurve=False, rootOnCurve=False, twistType='easeInOut', sj=jnt_list[0], ee=jnt_list[-1])

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
    
# parent the first and last clusters to ctrl   
pm.parent(cluster_list[0], cluster_list[1], start_ctrl)
pm.parent(cluster_list[-1], cluster_list[-2], end_ctrl)

# parent the joint to the first ctrl
pm.parent(jnt_list[0], start_ctrl)

mid_clust_grp = pm.group(em=True, name='mid_cluster_grp')
pm.parent(cluster_list[2], mid_clust_grp)
pm.pointConstraint(start_ctrl, end_ctrl, mid_clust_grp)


pm.parent(start_ctrl, end_ctrl, main_cable_grp)
follicle_parent = follicle.getParent()
pm.parent(mid_clust_grp, iks_handle, crv, result_spline_crv, follicle, misc_grp)
pm.delete(follicle_parent)
'''