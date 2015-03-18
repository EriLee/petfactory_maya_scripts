import pymel.core as pm


# one idea is to use a crv as a ref to get the length, and position of cv
# the map that out flat with an even spacing, create the crv rig, with joints etc
# create cable meash from duplicated geo, duplicate combine, merge, bind to the joints
# the move crv into position.


crv = pm.ls(sl=True)[0]

crv_shape = crv.getShape()

#dir(crv_shape)
degree = crv_shape.degree()
num_cvs = crv_shape.numCVs()
arc_length = pm.arclen(crv_shape)
num_joints = 10

u_inc = 1.0 / (num_joints-1)
jnt_list = []
for index in range(10):
    
    # create the joints
    jnt = pm.createNode('joint', name='jnt_{0}'.format(index), ss=True)
    jnt_list.append(jnt)
    pm.toggle(jnt, localAxis=True)
    
    # create the motion path node, if fractionMode is True it will use 0-1 u range
    mp = pm.pathAnimation(jnt, follow=True, bank=True, fractionMode=True, c=crv)
    
    # break the uvalue anim connection
    anim_crv = pm.listConnections('{0}.uValue'.format(mp))
    pm.delete(anim_crv)
    
    pm.setAttr('{0}.uValue'.format(mp), index*u_inc)
