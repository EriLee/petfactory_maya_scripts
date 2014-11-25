import pymel.core as pm

def create_round_corners(crv, name='smooth'):
    
    radius_a = 2
    radius_b = .75
    cv_list = crv.getShape().getCVs(space='world')
    num_cv = len(cv_list)
    
    crv_list = []


    crv_grp = pm.group(em=True, name='round_curve_group')
    
    for index, cv in enumerate(cv_list):
        
        if index is 0:
                lin_start_pos = cv_list[index]
                
        if index < num_cv-2:
      
            pos_a = ((cv_list[index] - cv_list[index+1]).normal())*radius_a + cv_list[index+1]
            pos_b = ((cv_list[index] - cv_list[index+1]).normal())*radius_b + cv_list[index+1]
            pos_c = ((cv_list[index+2] - cv_list[index+1]).normal())*radius_b + cv_list[index+1]
            pos_d = ((cv_list[index+2] - cv_list[index+1]).normal())*radius_a + cv_list[index+1]
    
            #create_loc(pos_a)
            #create_loc(pos_b)
            #create_loc(pos_c)
            #create_loc(pos_d)
            
            pos_list = (    [pos_a[0], pos_a[1], pos_a[2]],
                            [pos_b[0], pos_b[1], pos_b[2]],
                            [pos_c[0], pos_c[1], pos_c[2]],
                            [pos_d[0], pos_d[1], pos_d[2]],
            )
            
            pos_deg_1 = (    [lin_start_pos[0], lin_start_pos[1], lin_start_pos[2]],
                              [pos_a[0], pos_a[1], pos_a[2]]
            )
            
            # deg 1
            crv_list.append(pm.curve(degree=1, p=pos_deg_1, name='crv_{0}_{1}'.format(name, index)))
            
            # deg 3
            crv_list.append(pm.curve(degree=3, p=pos_list, name='crv_{0}_{1}'.format(name, index)))
                
                
            lin_start_pos = pos_d
            
        elif index < num_cv-1:
            
            pos_deg_1 = (    [lin_start_pos[0], lin_start_pos[1], lin_start_pos[2]],
                              [cv_list[index+1][0], cv_list[index+1][1], cv_list[index+1][2]]
            )
            
            # deg 1
            crv_list.append(pm.curve(degree=1, p=pos_deg_1, name='crv_{0}_{1}'.format(name, index)))
            
    pm.parent(crv_list, crv_grp)       
    return crv_list
            

def create_polygon_from_profile_list(profile_list): 
  
    num_profile = len(profile_list)
    num_profile_points = len(profile_list[0])
    polygon_list = []
    
    for index, profile in enumerate(profile_list):
        
        if index < num_profile-1:
            
            for p_index, vec in enumerate(profile):
                
                if p_index < num_profile_points-1:
                    
                    p_1 = profile_list[index+1][p_index]
                    p_2 = profile_list[index+1][p_index+1]
                    p_3 = profile_list[index][p_index+1]
                    p_4 = profile_list[index][p_index]
                    
                
                # on the last position we "wrap around" to the first index
                else:
                    p_1 = profile_list[index+1][p_index]
                    p_2 = profile_list[index+1][0]
                    p_3 = profile_list[index][0]
                    p_4 = profile_list[index][p_index]
                    
                    
                polygon = pm.polyCreateFacet(p=[p_1, p_2, p_3, p_4])
                polygon_list.append(polygon)
                

    mesh = pm.polyUnite(polygon_list, ch=False)
    pm.polyMergeVertex(mesh, d=0.15)
    pm.delete(mesh, ch=True)
    return mesh


    

def plot_pos_on_path(crv, num_step):
    ''' Helper function to generate the profile positions along a parth'''
    if not isinstance(crv, pm.nodetypes.NurbsCurve):

        try:
            crv = crv.getShape()
            if not isinstance(crv, pm.nodetypes.NurbsCurve):
                pm.warning('Please select a NurbsCurve!')
                return None
                
        except AttributeError as e:
            pm.warning('Please select a NurbsCurve!')
            return None
      
    pos_list = []
    
    min_u, max_u = crv.getKnotDomain()
    u_step = max_u / (num_step-1)
    
    for i in range(num_step):
        
        u = u_step * i
        pos_list.append(crv.getPointAtParam(u, space='world'))
          
    return pos_list


def rotate_profile(profile_list, profile_scale):
    
    profile_copy = profile_list[:]
    
    # matrix to rotate the profile
    # rotate around Z axis
    tm_z_neg = pm.datatypes.TransformationMatrix(   [[0,1,0,0],
                                                    [-1,0,0,0],
                                                    [0,0,1,0],
                                                    [0,0,0,1]
                                                    ])
    # rotate around Z axis                                        
    tm_z_pos = pm.datatypes.TransformationMatrix(   [[0,-1,0,0],
                                                    [1,0,0,0],
                                                    [0,0,1,0],
                                                    [0,0,0,1]
                                                    ])
        
    # rotate the profile vectors    
    for i, vec in enumerate(profile_copy):
        profile_copy[i] = vec.rotateBy(tm_z_pos) * profile_scale
    
    return profile_copy 
    
    
def create_profile_list(crv, num_step, profile_list, profile_scale=1):
    
    if not crv:
        pm.warning('Please seölect a NurbsCurve!')
        return None
        
    if not isinstance(crv, pm.nodetypes.NurbsCurve):

        try:
            crv = crv.getShape()
            if not isinstance(crv, pm.nodetypes.NurbsCurve):
                pm.warning('Please select a NurbsCurve!')
                return None
                
        except AttributeError as e:
            pm.warning('Please select a NurbsCurve!')
            return None
            
    
    min_u, max_u = crv.getKnotDomain()
    u_step = max_u / (num_step-1)

    profile_along_crv_list = []
    
    #print(min_u, max_u, u_step)
    
    pos_list = []
    for i in range(num_step):

        u = u_step * i
        pos_list.append(crv.getPointAtParam(u, space='world'))
        
    num_pos = len(pos_list)
    for index, pos in enumerate(pos_list):
        
        if index < num_pos-1:
            tangent = (pos_list[index] - pos_list[index+1]).normal()
        else:
            tangent = (pos_list[-2] - pos_list[-1]).normal()


        up = pm.datatypes.Vector(0,1,0)
        #print('normal {0}'.format(normal))
        
        
        cross = (tangent.cross(up)).normal()
        up_ortho = cross.cross(tangent)
        #print('cross {0}'.format(cross))
        
        
        tm = pm.datatypes.TransformationMatrix(    [tangent[0], tangent[1], tangent[2], 0],
                                                  [up_ortho[0], up_ortho[1], up_ortho[2], 0],
                                                  [cross[0], cross[1], cross[2], 0],
                                                  [pos[0], pos[1], pos[2], 1],
        )
        
        loc = pm.spaceLocator()
        loc.setMatrix(tm)
        
        
        temp_vec_list = []
        
        for profile in profile_list:
    
            vec_rot = profile.rotateBy(tm) + pos
            temp_vec_list.append(vec_rot)
            
        profile_along_crv_list.append(temp_vec_list)
  

    return profile_along_crv_list
        
 
#plot_pos_on_path(pm.ls(sl=True)[0], 10)

square_profile_list = [  pm.datatypes.Vector(-1,0,-1), pm.datatypes.Vector(1,0,-1), pm.datatypes.Vector(1,0,1), pm.datatypes.Vector(-1,0,1)]
circle_profile_list = [  pm.datatypes.Vector([2.77555756156e-17, 6.12323399574e-17, -1.0]),
                          pm.datatypes.Vector([-0.64281186962, 4.68914897419e-17, -0.765796142602]),
                          pm.datatypes.Vector([-0.984318988333, 1.06113414645e-17, -0.173296357315]),
                          pm.datatypes.Vector([-0.865130518476, -3.0600228022e-17, 0.499739648089]),
                          pm.datatypes.Vector([-0.341555358666, -5.74767756734e-17, 0.938666980772]),
                          pm.datatypes.Vector([0.341555358666, -5.74767756734e-17, 0.938666980772]),
                          pm.datatypes.Vector([0.865130518476, -3.0600228022e-17, 0.499739648089]),
                          pm.datatypes.Vector([0.984318988333, 1.06113414645e-17, -0.173296357315]),
                          pm.datatypes.Vector([0.64281186962, 4.68914897419e-17, -0.765796142602]),
                          pm.datatypes.Vector([2.77555756156e-17, 6.12323399574e-17, -1.0])]


# rotate the prpfile
roteted_profile = rotate_profile(circle_profile_list, 1)

'''
crv = None
sel_list = pm.ls(sl=True)
if sel_list:
    crv=sel_list[0]

'''
profile_list = create_profile_list(crv, 10, roteted_profile)


if profile_list:
    create_polygon_from_profile_list(profile_list)

# build rounded curves
sel_list = pm.ls(sl=True)
crv_list = create_round_corners(crv=sel_list[0], name='round')

    
def create_from_multiple_crv(crv_list, profile_list):

    mesh_list = []
    
    for index, crv in enumerate(crv_list):
        #print(index)
        profile_list = create_profile_list(crv, 5, roteted_profile)
    
        if profile_list:
            mesh = create_polygon_from_profile_list(profile_list)
            mesh_list.append(mesh)
        
    mesh = pm.polyUnite(mesh_list, ch=False)
    pm.polyMergeVertex(mesh, d=0.15)
    pm.delete(mesh, ch=True)
    
create_from_multiple_crv(crv_list, roteted_profile)       
        

