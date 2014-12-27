import pymel.core as pm


def t_matrix_on_path(pos_list):
        
    tm_list = []
    for index, pos in enumerate(pos_list):

        if index > 0:

            prev_pos = pos_list[index-1]
            curr_pos = pos

            aim_vec = (curr_pos - prev_pos).normal()
            up_vec = pm.datatypes.Vector(0,1,0)
            

            # if the aim and up vec are effectively (within a certain tolerance) colinear, the
            # resulting perpendicualar vector will not be vaild in this case the negative z axis
            # will be used as up vector
            if aim_vec.isParallel(up_vec, tol=0.1):

                print('z up', index)
                up_vec = pm.datatypes.Vector(1,0,0)
                
                cross_vec = aim_vec.cross(up_vec).normal()
                up_vec_ortho = cross_vec.cross(aim_vec)
                
                tm = pm.datatypes.TransformationMatrix(    [aim_vec[0], aim_vec[1], aim_vec[2], 0],
                                                           [up_vec_ortho[0], up_vec_ortho[1], up_vec_ortho[2], 0],
                                                           [cross_vec[0], cross_vec[1], cross_vec[2], 0], 
                                                           [prev_pos[0], prev_pos[1], prev_pos[2], 1])            
            else:
                #print('y up')
                cross_vec = aim_vec.cross(up_vec).normal()
                up_vec_ortho = cross_vec.cross(aim_vec)
                tm = pm.datatypes.TransformationMatrix(    [aim_vec[0], aim_vec[1], aim_vec[2], 0], 
                                                           [up_vec_ortho[0], up_vec_ortho[1], up_vec_ortho[2], 0],
                                                           [cross_vec[0], cross_vec[1], cross_vec[2], 0],
                                                           [prev_pos[0], prev_pos[1], prev_pos[2], 1])


            if index is num_pos-1:
                tm_list.append(tm)
                tm = pm.datatypes.TransformationMatrix(tm.asRotateMatrix())
                tm.addTranslation(curr_pos, space='world')
                tm_list.append(tm)


            else:
                tm_list.append(tm)
            
            '''  
            z_axis = pm.datatypes.Vector(tm[2][0], tm[2][1], tm[2][2])
            
            
            test_vec = pm.datatypes.Vector(0,0,1)
            
            z_dir =  'pos' if z_axis.dot(test_vec) > 0 else 'neg'
            sp = pm.polySphere(r=.05, name='sp_{0}_{1}'.format(z_dir, index))[0]
            sp.translate.set(z_axis)
            
            print(z_axis)
            '''

    return tm_list

def get_pos_on_crv(crv, num_pos):
    
    crv_shape = crv.getShape()
    crv_length = crv_shape.length()
    length_inc = float(crv_length) / (num_pos-1)
    
    pos_list = []
    for n in range(num_pos):
        u = crv_shape.findParamFromLength(length_inc * n)
        p = crv_shape.getPointAtParam(u, space='world')
        pos_list.append(p)

    return pos_list

def move_ascending_cv(crv, amount=1):
    
    crv_shape = crv.getShape()
    cv_list = crv_shape.getCVs()
    
    for index, cv in enumerate(cv_list):
        print(cv)
        crv_shape.setCV(index, (cv[0], cv[1]+index*amount, cv[2]), space='world')
    crv.updateCurve()



num_pos = 100
crv = pm.PyNode('curve1')

# get pos on crv
pos_list = get_pos_on_crv(crv, num_pos)

# get tm list
tm_list = t_matrix_on_path(pos_list)

def viz(tm_list):
    p_grp = pm.group(em=True)
    for tm in tm_list:
        #sp = pos(p)
        sp = pm.polySphere(r=.05)[0]
        sp.setMatrix(tm)
        pm.toggle(localAxis=True)
        pm.parent(sp, p_grp)

viz(tm_list)

#move_ascending_cv(crv, amount=-1)