pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/spring_jnts.mb', f=True)

mel.eval('ikSpringSolver')

name = 'cable_rig'
ik_jnt_list = [pm.PyNode('joint{0}'.format(j+1)) for j in range(5)]

ik_handle, ik_effector = pm.ikHandle(sj=ik_jnt_list[0], ee=ik_jnt_list[-1], n='{0}_ikh'.format(name), solver='ikSpringSolver')

start_ctrl = pm.circle(n='start', ch=False)[0]
end_ctrl = pm.circle(n='end', ch=False)[0]

start_ctrl.setMatrix(ik_jnt_list[0].getMatrix(ws=True))
end_ctrl.setMatrix(ik_jnt_list[-1].getMatrix(ws=True))

pm.parent(ik_handle, end_ctrl)

dist = pm.distanceDimension(sp=ik_jnt_list[0].getTranslation(space='world'), ep=ik_jnt_list[-1].getTranslation(space='world'))
dist_transform = dist.getParent()
dist_transform.rename('{0}_dist'.format(name))
start_loc = pm.listConnections( '{0}.startPoint'.format(dist))[0]
start_loc.rename('start_loc')
end_loc = pm.listConnections( '{0}.endPoint'.format(dist))[0]
end_loc.rename('end_loc')

pm.parent(start_loc, start_ctrl)
pm.parent(end_loc, end_ctrl)