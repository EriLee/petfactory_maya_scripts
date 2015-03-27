def set_curve_skin_percent(crv, jnt_list, skin_cluster, num_div):
    
    crv_shape = crv.getShape()
    num_jnt = len(jnt_list)
    
    if crv_shape.numCVs() is not (num_jnt + (num_jnt-1)*num_div):
        pm.warning('The number of CVs is not valid')
        return None
        
    # Turn off skinweight normalization and reset skinweights
    skin_cluster.setNormalizeWeights(0)
    pm.skinPercent(skin_cluster, crv_shape, nrm=False, prw=100)
     
    cv_index = 0
    u_inc = 1.0 / (num_div + 1)
    
    pm.skinPercent(skin_cluster, crv_shape, nrm=False, prw=100)
    
    for index in range(num_jnt-1):
        
        start = jnt_list[index]
        end = jnt_list[index+1]

        for n in range(num_div+1):
            u = u_inc * n
            pm.skinPercent(skin_cluster, '{0}.cv[{1}]'.format(crv, cv_index), transformValue=('{0}'.format(start), 1.0-u))
            pm.skinPercent(skin_cluster, '{0}.cv[{1}]'.format(crv, cv_index), transformValue=('{0}'.format(end), u))
            cv_index +=1
            
    pm.skinPercent(skin_cluster, '{0}.cv[{1}]'.format(crv, cv_index), transformValue=('{0}'.format(jnt_list[-1]), 1.0))