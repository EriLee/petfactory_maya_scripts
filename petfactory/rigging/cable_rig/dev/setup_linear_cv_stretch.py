import petfactory.rigging.ik_setup.stretchy_ik as stretchy_ik
reload(stretchy_ik)

    
pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/spring_jnts.mb', f=True)

name = 'cable_rig'
ik_jnt_list = [pm.PyNode('joint{0}'.format(j+1)) for j in range(5)]

# create the ctrl
start_ctrl = pm.circle(n='{0}_start_ctrl'.format(name), ch=False)[0]
end_ctrl = pm.circle(n='{0}_end_ctrl'.format(name), ch=False)[0]


sprink_ik_dict = stretchy_ik.create_ik_spring(  ik_jnt_list=ik_jnt_list,
                                                start_ctrl=start_ctrl,
                                                end_ctrl=end_ctrl,
                                                name=name)



dist = sprink_ik_dict['distance_shape']
total_jnt_length = sprink_ik_dict['total_jnt_length']
stretch_per_jnt_md = sprink_ik_dict['stretch_per_jnt_md']
stretch_condition = sprink_ik_dict['stretch_condition']

num_div = 1

crv_lin = pm.curve(d=1, p=[(0,0,0), (0,0,0), (0,0,0)])
crv_lin_shape = crv_lin.getShape()

stretch_per_cv_md = pm.createNode('multiplyDivide', n='stretch_per_cv_md')
stretch_per_cv_md.operation.set(2)
stretch_per_jnt_md.outputX >> stretch_per_cv_md.input1X
stretch_per_cv_md.input2X.set(num_div+1)


# calculate the ditsnace between the jnts
dist_btw_jnt = (ik_jnt_list[0].getTranslation(ws=True) - ik_jnt_list[1].getTranslation(ws=True)).length()

# calculate the distnce btw the cvs
dist_btw_cv = dist_btw_jnt / (num_div+1)

cv_dist_pma = pm.createNode('plusMinusAverage', n='cv_dist_pma')
cv_dist_pma.input1D[0].set(dist_btw_cv)
stretch_per_cv_md.outputX >> cv_dist_pma.input1D[1]

cv_dist_cho = pm.createNode('choice', n='cv_dist_cho')
cv_dist_pma.output1D >> cv_dist_cho.input[0]
cv_dist_cho.input[1].set(dist_btw_cv)

stretch_condition.outColorR >> cv_dist_cho.selector


cv_pos_vec_prod = pm.createNode('vectorProduct', n='cv_pos_vec_prod')
cv_pos_vec_prod.operation.set(4)
cv_dist_cho.output >> cv_pos_vec_prod.input1X

ik_jnt_list[0].worldMatrix[0] >> cv_pos_vec_prod.matrix

cv_pos_vec_prod.output >> crv_lin_shape.controlPoints[0]

'''
cho = pm.PyNode('choice1')
cho.input[1].set(3.5355)
                                                
pma = pm.PyNode('plusMinusAverage1')
pma.input1D[1].set(3.5355)
'''