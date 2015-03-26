pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/spring_jnts.mb', f=True)

ik_jnt_list = [pm.PyNode('joint{0}'.format(j+1)) for j in range(5)]

pos_list  = [j.getTranslation(ws=True) for j in ik_jnt_list]

crv = pm.curve(d=1, p=pos_list)
crv_shape = crv.getShape()

crv_shape.overrideEnabled.set(1)
crv_shape.overrideColor.set(17)

pm.toggle(crv, controlVertex=True)

skin_cluster = pm.skinCluster(ik_jnt_list[0], crv)


def set_curve_skin_percent(crv, jnt_list, skin_cluster, num_div):

    num_jnt = len(jnt_list)
    cv_index = 0
    u_inc = 1.0 / (num_div + 1)
    for index in range(num_jnt-1):
        
        start = jnt_list[index]
        end = jnt_list[index+1]

        for n in range(num_div+1):
            u = u_inc * n
            pm.skinPercent(skin_cluster, '{0}.cv[{1}]'.format(crv, cv_index), transformValue=('{0}'.format(start), 1.0-u))
            pm.skinPercent(skin_cluster, '{0}.cv[{1}]'.format(crv, cv_index), transformValue=('{0}'.format(end), u))
            
            cv_index +=1
            
    pm.skinPercent(skin_cluster, '{0}.cv[{1}]'.format(crv, cv_index), transformValue=('{0}'.format(jnt_list[-1]), 1.0))
    
num_div = 0
set_curve_skin_percent(crv=crv, jnt_list=ik_jnt_list, skin_cluster=skin_cluster, num_div=num_div)