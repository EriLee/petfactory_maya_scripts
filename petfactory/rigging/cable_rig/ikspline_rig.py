import pymel.core as pm

pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)

# one idea is to use a crv as a ref to get the length, and position of cv
# the map that out flat with an even spacing, create the crv rig, with joints etc
# create cable meash from duplicated geo, duplicate combine, merge, bind to the joints
# the move crv into position.

num_joints = 10
jnt_list = []

# the crv, should be 3 degree, with 5 cvs
crv = pm.curve(d=3, ep=[(-5, 0, 0), (0, 0, 0), (5, 0, 0)])

# create a crv info
crv_info = pm.arclen(crv, ch=True)


crv_shape = crv.getShape()
min_u, max_u = crv_shape.getKnotDomain()


# setup the joint stretch, divide the crv length with the number of joints to
# to get a value of how much to scale each joint to reach the full crv length
# the output from the mult double linear will be fed into the scale x of the jnts
mult_double = pm.createNode('multDoubleLinear')
crv_info.arcLength >> mult_double.input1
mult_double.input2.set(1.0/num_joints)

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
    mult_double.output >> jnt.scaleX
    
    # parent the jnt
    if index > 0:
        pm.parent(jnt, jnt_list[index-1])
    

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

# create and position the start and end ctrl
start_ctrl = pm.circle(normal=(1,0,0), name='start')[0]
start_ctrl.setMatrix(jnt_list[0].getMatrix(ws=True))

end_ctrl = pm.circle(normal=(1,0,0), name='end')[0]
end_ctrl.setMatrix(jnt_list[-1].getMatrix(ws=True))

# set the world up objects
start_ctrl.worldMatrix[0] >> iks_handle.dWorldUpMatrix
end_ctrl.worldMatrix[0] >> iks_handle.dWorldUpMatrixEnd



num_cvs = crv_shape.numCVs()

# add cluster to cvs. The first cluster will have first and second cv the mid cv will have one
# cluster to it self and the last cluster will have to cvs.
cluster_list = []
for i in range(num_cvs-2):
    
    if i is 0:
        cv = '0:1'
        
    elif i > num_cvs-4:
        cv = '{0}:{1}'.format(num_cvs-2, num_cvs-1)
        
    else:
        cv = str(i+1)

    clust, clust_handle = pm.cluster('{0}.cv[{1}]'.format(crv_shape.longName(), cv), relative=False, name='{0}_{1}_cluster_'.format('test', i))
    cluster_list.append(clust_handle)
    
# parent the first and last clusters to ctrl   
pm.parent(cluster_list[0], start_ctrl)
pm.parent(cluster_list[-1], end_ctrl)

# parent the joint to the first ctrl
pm.parent(jnt_list[0], start_ctrl)

mid_clust_grp = pm.group(em=True, name='mid_cluster_grp')
pm.parent(cluster_list[1], mid_clust_grp)

pm.pointConstraint(start_ctrl, end_ctrl, mid_clust_grp)