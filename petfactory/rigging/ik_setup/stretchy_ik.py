pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/spring_jnts.mb', f=True)

mel.eval('ikSpringSolver')

name = 'cable_rig'

# the ik jnt list
ik_jnt_list = [pm.PyNode('joint{0}'.format(j+1)) for j in range(5)]

# the jnts to make stretchy
stretch_jnt_list = ik_jnt_list[1:]

# add ik handle    
ik_handle, ik_effector = pm.ikHandle(sj=ik_jnt_list[0], ee=ik_jnt_list[-1], n='{0}_ikh'.format(name), solver='ikSpringSolver')

# add ctrls
start_ctrl = pm.circle(n='start', ch=False)[0]
end_ctrl = pm.circle(n='end', ch=False)[0]

#position the ctrl
start_ctrl.setMatrix(ik_jnt_list[0].getMatrix(ws=True))
end_ctrl.setMatrix(ik_jnt_list[-1].getMatrix(ws=True))

ik_jnt_grp = pm.group(em=True, parent=start_ctrl, n='{0}_ik_jnt_grp'.format(name))
start_ctrl_hidden_grp = pm.group(em=True, parent=start_ctrl, n='{0}_start_ctrl_hidden_grp'.format(name))
end_ctrl_hidden_grp = pm.group(em=True, parent=end_ctrl, n='{0}_end_ctrl_hidden_grp'.format(name))

# measure the distance between the start and end ctrl
dist = pm.distanceDimension(sp=ik_jnt_list[0].getTranslation(space='world'), ep=ik_jnt_list[-1].getTranslation(space='world'))
dist_transform = dist.getParent()
dist_transform.rename('{0}_dist'.format(name))
start_loc = pm.listConnections( '{0}.startPoint'.format(dist))[0]
start_loc.rename('{0}_start_loc'.format(name))
end_loc = pm.listConnections( '{0}.endPoint'.format(dist))[0]
end_loc.rename('{0}_end_loc'.format(name))

pm.parent(dist_transform, start_loc, start_ctrl_hidden_grp)
pm.parent(ik_handle, end_loc, end_ctrl_hidden_grp)


# get the total length of the joint chain
total_jnt_length = 0
for jnt in stretch_jnt_list:
    total_jnt_length += jnt.tx.get()

# create a cond node to compute when we neeed to stretch
stretch_cnd = pm.createNode('condition', n='{0}_stretch_cnd'.format(name))
dist.distance >> stretch_cnd.firstTerm
stretch_cnd.secondTerm.set(total_jnt_length)
stretch_cnd.operation.set(2)

# get the differance between the curr length and the total jonit chain length
length_diff_pma = pm.createNode('plusMinusAverage', n='{0}_length_diff_pma'.format(name))
length_diff_pma.operation.set(2)
dist.distance >> length_diff_pma.input1D[0]
length_diff_pma.input1D[1].set(total_jnt_length)
    
# calculate how much each jnt need to stretch
stretch_per_jnt_md = pm.createNode('multiplyDivide', n='{0}_stretch_per_jnt_md'.format(name))
stretch_per_jnt_md.operation.set(2)
length_diff_pma.output1D >> stretch_per_jnt_md.input1.input1X
stretch_per_jnt_md.input2.input2X.set(len(stretch_jnt_list))


for jnt in stretch_jnt_list:
    
    # create a pms node per stretch joint to compute the result length
    jnt_result_length_pma = pm.createNode('plusMinusAverage', n='{0}_{1}_length_pma'.format(name, jnt.name()))
    jnt_result_length_pma.input1D[0].set(jnt.tx.get())
    stretch_per_jnt_md.outputX >> jnt_result_length_pma.input1D[1]
    
    jnt_choice = pm.createNode('choice', n='{0}_{1}_cho'.format(name, jnt.name()))
    jnt_result_length_pma.output1D >> jnt_choice.input[0]
    jnt_choice.input[1].set(jnt.tx.get())
    
    stretch_cnd.outColorR >> jnt_choice.selector
    jnt_choice.output >> jnt.tx


# add polevector
vec_prod = pm.createNode('vectorProduct', n='{0}_polevec_vp'.format(name))
# the pole vector expects a vector, so we set the operation to vector matrix product
vec_prod.operation.set(3)
start_ctrl.worldMatrix[0] >> vec_prod.matrix
vec_prod.input1.set(0,0,1)
vec_prod.output >> ik_handle.poleVector

pm.addAttr(start_ctrl, ln='ik_twist', at='double', k=True, defaultValue=0)
pm.addAttr(start_ctrl, ln='ik_twist_offset', at='double', k=False, defaultValue=-90)


# create a ik twist ctrl
ik_twist_pma = pm.createNode('plusMinusAverage', n='{0}_ik_twist_pma'.format(name))
start_ctrl.ik_twist_offset >> ik_twist_pma.input1D[0]
start_ctrl.ik_twist >> ik_twist_pma.input1D[1]
ik_twist_pma.output1D >> ik_handle.twist


pm.parent(ik_jnt_list[0], ik_jnt_grp)
pm.setAttr(start_ctrl_hidden_grp.v, 0, lock=True)
pm.setAttr(end_ctrl_hidden_grp.v, 0, lock=True)
