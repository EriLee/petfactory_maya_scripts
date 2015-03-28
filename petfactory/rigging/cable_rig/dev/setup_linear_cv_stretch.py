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
stretch_btw_jnt_md = sprink_ik_dict['stretch_per_jnt_md']
stretch_condition = sprink_ik_dict['stretch_condition']




num_div = 2
num_jnt = len(ik_jnt_list)
num_cvs = num_jnt + (num_jnt-1)*num_div


crv_lin_pos = [(j,0,0) for j in range(num_cvs)]
crv_lin = pm.curve(d=1, p=crv_lin_pos)
crv_lin_shape = crv_lin.getShape()
pm.toggle(crv_lin_shape, cv=True)




jnt_index = 0
for cv in range(num_cvs):
    cv_index = cv % (num_div+1)
    
    if cv_index is 0:
        curr_jnt = ik_jnt_list[jnt_index]
        
        # connect the cv that lies directly on a joint
        cv_pos_vec_prod = pm.createNode('vectorProduct', n='cv_{0}_pos_vec_prod'.format(cv))
        cv_pos_vec_prod.operation.set(4)
        ik_jnt_list[jnt_index].worldMatrix[0] >> cv_pos_vec_prod.matrix
        cv_pos_vec_prod.output >> crv_lin_shape.controlPoints[cv]
        
        # check the distance to the next joint, if we are not on the last cv
        if cv is not (num_cvs-1):
            
            # calculate the jnt length
            dist_btw_jnt = (ik_jnt_list[jnt_index+1].getTranslation(ws=True) - ik_jnt_list[jnt_index].getTranslation(ws=True)).length()
            # calculate the distnce btw the cvs
            dist_btw_cv = dist_btw_jnt / (num_div+1)

            # create a node to give the distance btw th cvs per joint
            stretch_btw_cv_md = pm.createNode('multiplyDivide', n='stretch_btw_cv_jnt_{0}_md'.format(jnt_index))
            stretch_btw_cv_md.operation.set(2)
            stretch_btw_jnt_md.outputX >> stretch_btw_cv_md.input1X
            stretch_btw_cv_md.input2X.set(num_div+1)
            
        jnt_index += 1
        
        
    else:
        
        cv_dist_pma = pm.createNode('plusMinusAverage', n='cv_{0}_dist_pma'.format(cv))
        cv_dist_pma.input1D[0].set(dist_btw_cv * cv_index)
        
        # if the cv index is greater than 1 we need to multiply the length of the dist btw cv
        if cv_index > 1:
            cv_dist_multiplier = pm.createNode('multDoubleLinear',n='cv_{0}_cv_dist_multiplier_mdl'.format(cv))
            stretch_btw_cv_md.outputX >> cv_dist_multiplier.input1
            cv_dist_multiplier.input2.set(cv_index)
            cv_dist_multiplier.output >> cv_dist_pma.input1D[1]
            
        # on the second cv (when cv_index is 1) after each joint we do not need to multiply the result
        else:
            stretch_btw_cv_md.outputX >> cv_dist_pma.input1D[1]
            
        cv_dist_cho = pm.createNode('choice', n='cv_{0}_dist_cho'.format(cv))
        cv_dist_pma.output1D >> cv_dist_cho.input[0]
        cv_dist_cho.input[1].set(dist_btw_cv * cv_index)
        
        stretch_condition.outColorR >> cv_dist_cho.selector
        
        cv_pos_vec_prod = pm.createNode('vectorProduct', n='cv_{0}_pos_vec_prod'.format(cv))
        cv_pos_vec_prod.operation.set(4)
        cv_dist_cho.output >> cv_pos_vec_prod.input1X
        
        ik_jnt_list[jnt_index-1].worldMatrix[0] >> cv_pos_vec_prod.matrix
        cv_pos_vec_prod.output >> crv_lin_shape.controlPoints[cv]

