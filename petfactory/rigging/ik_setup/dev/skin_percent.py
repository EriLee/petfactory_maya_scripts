def interpolate_positions(pos_list, num_divisions=1):
    
    u_inc = 1.0 / (num_divisions+1)
    last_index = len(pos_list)-1
    
    ret_pos_list = []
    for index, pos in enumerate(pos_list):
        
        if index < last_index:
            
            dx = pos_list[index+1][0] - pos_list[index][0]
            dy = pos_list[index+1][1] - pos_list[index][1]
            dz = pos_list[index+1][2] - pos_list[index][2]
            
            for u in range(num_divisions+1):
                ret_pos_list.append((   pos_list[index][0] + dx*u*u_inc,
                                        pos_list[index][1] + dy*u*u_inc,
                                        pos_list[index][2] + dz*u*u_inc))
    
        else:
            ret_pos_list.append(pos_list[-1])
    
    return ret_pos_list
    
    
def set_curve_skin_percent(crv, jnt_list, skin_cluster):
    
    crv_shape = crv.getShape()
    num_jnt = len(jnt_list)
    num_cvs = crv_shape.numCVs() 
        
    cvs_per_bone = float(num_cvs - num_jnt) / (num_jnt-1)
    
    # check if we have a valid number of cvs
    if cvs_per_bone % 1 == 0:
        
        num_div = int(cvs_per_bone)    
    
    else:
        pm.warning('The number of cvs are not valid!')
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
    


pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/spring_3_jnts.mb', f=True)

ik_jnt_list = [pm.PyNode('joint{0}'.format(j+1)) for j in range(3)]

jnt_pos_list  = [j.getTranslation(ws=True) for j in ik_jnt_list]

num_div = 2

pos_list = interpolate_positions(pos_list=jnt_pos_list, num_divisions=num_div)

crv = pm.curve(d=1, p=pos_list)
crv_shape = crv.getShape()

crv_shape.overrideEnabled.set(1)
crv_shape.overrideColor.set(17)

pm.toggle(crv, controlVertex=True)

skin_cluster = pm.skinCluster(crv, ik_jnt_list[0])

set_curve_skin_percent(crv=crv, jnt_list=ik_jnt_list, skin_cluster=skin_cluster)