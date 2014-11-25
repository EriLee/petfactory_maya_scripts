import pymel.core as pm
import pprint

def create_round_corners(crv, inner_radius=.5, outer_radius=1, name='smooth'):
    

    cv_list = crv.getShape().getCVs(space='world')
    num_cv = len(cv_list)
    
    #crv_list = []
    crv_cv_list = []


    #crv_grp = pm.group(em=True, name='round_curve_group')
    
    for index, cv in enumerate(cv_list):
        
        if index is 0:
                lin_start_pos = cv_list[index]
                
        if index < num_cv-2:
      
            pos_a = ((cv_list[index] - cv_list[index+1]).normal())*outer_radius + cv_list[index+1]
            pos_b = ((cv_list[index] - cv_list[index+1]).normal())*inner_radius + cv_list[index+1]
            pos_c = ((cv_list[index+2] - cv_list[index+1]).normal())*inner_radius + cv_list[index+1]
            pos_d = ((cv_list[index+2] - cv_list[index+1]).normal())*outer_radius + cv_list[index+1]
    
            #create_loc(pos_a)
            #create_loc(pos_b)
            #create_loc(pos_c)
            #create_loc(pos_d)
            
            pos_list = (    #[pos_a[0], pos_a[1], pos_a[2]],
                            [pos_b[0], pos_b[1], pos_b[2]],
                            [pos_c[0], pos_c[1], pos_c[2]],
                            #[pos_d[0], pos_d[1], pos_d[2]],
            )
            
            pos_deg_1 = (    [lin_start_pos[0], lin_start_pos[1], lin_start_pos[2]],
                              [pos_a[0], pos_a[1], pos_a[2]]
            )
            
            # deg 1
            #crv_list.append(pm.curve(degree=1, p=pos_deg_1, name='crv_{0}_{1}'.format(name, index)))
            crv_cv_list.append(pos_deg_1)
            
            # deg 3
            #crv_list.append(pm.curve(degree=3, p=pos_list, name='crv_{0}_{1}'.format(name, index)))
            crv_cv_list.append(pos_list)    
                
            lin_start_pos = pos_d
            
        elif index < num_cv-1:
            
            pos_deg_1 = (    [lin_start_pos[0], lin_start_pos[1], lin_start_pos[2]],
                              [cv_list[index+1][0], cv_list[index+1][1], cv_list[index+1][2]]
            )
            
            # deg 1
            #crv_list.append(pm.curve(degree=1, p=pos_deg_1, name='crv_{0}_{1}'.format(name, index)))
            crv_cv_list.append(pos_deg_1)
            
    #pm.parent(crv_list, crv_grp)       
    return crv_cv_list
    
'''
try:
    pm.delete('round_curve_group')
except pm.MayaNodeError as e:
    print(e)
'''
  
#crv = pm.ls(sl=True)[0]
crv_cv_list = create_round_corners(crv)

pos_list = []
for crv_cv in crv_cv_list:
    for pos in crv_cv:
        pos_list.append(pos)
   
pm.curve(degree=3, p=pos_list, name="smooth")