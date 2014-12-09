import pymel.core as pm

pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)

# one idea is to use a crv as a ref to get the length, and position of cv
# the map that out flat with an even spacing, create the crv rig, with joints etc
# create cable meash from duplicated geo, duplicate combine, merge, bind to the joints
# the move crv into position.

num_joints = 10
jnt_list = []

crv = pm.curve(d=3, ep=[(-5, 0, 0), (0, 0, 0), (5, 0, 0)])

# create a crv info
crv_info = pm.arclen(crv, ch=True)

mult_double = pm.createNode('multDoubleLinear')
crv_info.arcLength >> mult_double.input1

mult_double.input2.set(1.0/num_joints)




crv_shape = crv.getShape()
min_u, max_u = crv_shape.getKnotDomain()

u_inc = max_u / (num_joints-1)

for index in range(num_joints):
    
    pos = crv_shape.getPointAtParam(u_inc * index, space='world')

    # create the joints
    jnt = pm.createNode('joint', name='jnt_{0}'.format(index), ss=True)
    jnt_list.append(jnt)
    jnt.translate.set(pos)
    pm.toggle(jnt, localAxis=True)
    
    mult_double.output >> jnt.scaleX
    
    # parent the jnt
    if index > 0:
        pm.parent(jnt, jnt_list[index-1])
    

iks_handle, effector = pm.ikHandle(solver='ikSplineSolver', curve=crv, parentCurve=False, createCurve=False, rootOnCurve=False, twistType='easeInOut', sj=jnt_list[0], ee=jnt_list[-1])

# enable the advamced twist controls
iks_handle.dTwistControlEnable.set(1)
iks_handle.dWorldUpType.set(4)

# set the up axis to +z
iks_handle.dWorldUpAxis.set(3)

# set the up vector and up vector 2 to z
iks_handle.dWorldUpVector.set(0,0,1)
iks_handle.dWorldUpVectorEnd.set(0,0,1)

start_ctrl = pm.circle(normal=(1,0,0), name='start')[0]
start_ctrl.setMatrix(jnt_list[0].getMatrix(ws=True))
start_ctrl.worldMatrix[0] >> iks_handle.dWorldUpMatrix

end_ctrl = pm.circle(normal=(1,0,0), name='end')[0]
end_ctrl.setMatrix(jnt_list[-1].getMatrix(ws=True))
end_ctrl.worldMatrix[0] >> iks_handle.dWorldUpMatrixEnd



num_cvs = crv_shape.numCVs()
  
# loop through the cv and add cluster. On cv 0-1 add one cluster,
# the rest of the cv will have one cluster each, 
# might add one to the second to last and last
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
    
    
pm.parent(cluster_list[0], start_ctrl)
pm.parent(jnt_list[0], start_ctrl)

pm.parent(cluster_list[-1], end_ctrl)
