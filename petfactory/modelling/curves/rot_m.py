import pymel.core as pm
 
def create_polygon_from_profile_list(profile_list): 
  
    num_profile = len(profile_list)
    num_profile_points = len(profile_list[0])
    polygon_list = []
    
    for index, profile in enumerate(profile_list):
        
        if index < num_profile-1:
            #pm.polyCreateFacet(p=[profile[0], profile[1], profile[2], profile[3]])
            
            for p_index, vec in enumerate(profile):
                #sp = pm.polySphere(r=.1, name='vec_{0}_{1}'.format(index, p_index))[0]
                #sp.translate.set(vec)
                
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
    pm.polyMergeVertex(d=0.15)
    
                
        


# build the profile list
#profile_list = []
#for i in range(10):
    
#    profile_list.append([pm.datatypes.Vector(-1,i,-1), pm.datatypes.Vector(1,i,-1), pm.datatypes.Vector(1,i,1), pm.datatypes.Vector(-1,i,1)])
 
 
# create the polygons
#create_polygon_from_profile_list(profile_list)

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


def plot_pos_on_path(crv, num_step):
    
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
    
def create_profile_list(crv, num_step, profile_list, profile_scale=1):
    
    if not isinstance(crv, pm.nodetypes.NurbsCurve):

        try:
            crv = crv.getShape()
            if not isinstance(crv, pm.nodetypes.NurbsCurve):
                pm.warning('Please select a NurbsCurve!')
                return None
                
        except AttributeError as e:
            pm.warning('Please select a NurbsCurve!')
            return None
            

    
    # matrix to rotate the profile
    # rotate around Z axis
    tm_z_neg = pm.datatypes.TransformationMatrix(    [[0,1,0,0],
                                                [-1,0,0,0],
                                                [0,0,1,0],
                                                [0,0,0,1]
                                                ])
    # rotate around Z axis                                        
    tm_z_pos = pm.datatypes.TransformationMatrix(    [[0,-1,0,0],
                                                [1,0,0,0],
                                                [0,0,1,0],
                                                [0,0,0,1]
                                                ])
    
    # rotate the profile vectors    
    for i, vec in enumerate(profile_list):
        profile_list[i] = vec.rotateBy(tm_z_neg) * profile_scale
        
    
    
    min_u, max_u = crv.getKnotDomain()
    u_step = max_u / (num_step-1)

    profile_along_crv_list = []
    
    for i in range(num_step):
        
        #print(i)
        u = u_step * i
        pos = crv.getPointAtParam(u, space='world')
        #print('pos {0}'.format(pos))
        
        tangent = crv.tangent(u, space='world')
        #print('tangent {0}'.format(tangent))
        
        normal = crv.normal(u, space='world')
        #print('normal {0}'.format(normal))
        
        cross = tangent.cross(normal)
        #print('cross {0}'.format(cross))
        
        tm = pm.datatypes.TransformationMatrix(    [tangent[0], tangent[1], tangent[2], 0],
                                                  [normal[0], normal[1], normal[2], 0],
                                                  [cross[0], cross[1], cross[2], 0],
                                                  [pos[0], pos[1], pos[2], 1],
        
        )
        
        pos = pm.datatypes.Vector(tm[3][0], tm[3][1], tm[3][2])
        
        temp_vec_list = []
        
        for profile in profile_list:
    
            vec_rot = profile.rotateBy(tm) + pos
            temp_vec_list.append(vec_rot)
            
        profile_along_crv_list.append(temp_vec_list)
        
    return profile_along_crv_list
        
 
#plot_pos_on_path(pm.ls(sl=True)[0], 10)  
 
crv_t = pm.ls(sl=True)[0]
profile_list = create_profile_list(crv_t, 10, circle_profile_list)

if profile_list:
    create_polygon_from_profile_list(profile_list)

    

'''
import pymel.core as pm


m_1 = [  [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1],
]


#m_1 = pm.ls(sl=True)[0].getMatrix(worldSpace=True)
tm = pm.datatypes.TransformationMatrix(m_1)
pos = tm.getTranslation(space='world')

vec_a = pm.datatypes.Vector(-1,0,-1);
vec_b = pm.datatypes.Vector(1,0,-1);
vec_c = pm.datatypes.Vector(1,0,1);
vec_d = pm.datatypes.Vector(-1,0,1);

vec_a_rot = vec_a.rotateBy(tm) + pos
vec_b_rot = vec_b.rotateBy(tm) + pos
vec_c_rot = vec_c.rotateBy(tm) + pos
vec_d_rot = vec_d.rotateBy(tm) + pos

loc = pm.spaceLocator()
loc.translate.set(vec_a_rot)

loc = pm.spaceLocator()
loc.translate.set(vec_b_rot)

loc = pm.spaceLocator()
loc.translate.set(vec_c_rot)

loc = pm.spaceLocator()
loc.translate.set(vec_d_rot)

pm.polyCreateFacet(p=[vec_a_rot, vec_b_rot, vec_c_rot, vec_d_rot])
'''