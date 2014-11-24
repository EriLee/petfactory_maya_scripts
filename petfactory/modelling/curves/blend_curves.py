import pymel.core as pm

def create_loc(pos):
    loc = pm.spaceLocator()
    loc.translate.set(pos)
    loc.localScale.set(.2,.2,.2)
    

def create_round_corners(crv, name='smooth'):
    
    radius_a = 2
    radius_b = .75
    cv_list = crv.getShape().getCVs(space='world')
    num_cv = len(cv_list)


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
            pm.curve(degree=1, p=pos_deg_1, name='name')
            
            # deg 3
            pm.curve(degree=3, p=pos_list, name='name')
                
                
            lin_start_pos = pos_d
            
        elif index < num_cv-1:
            
            pos_deg_1 = (    [lin_start_pos[0], lin_start_pos[1], lin_start_pos[2]],
                              [cv_list[index+1][0], cv_list[index+1][1], cv_list[index+1][2]]
            )
            
            # deg 1
            pm.curve(degree=1, p=pos_deg_1, name=name)
            
          
            
sel_list = pm.ls(sl=True)

create_round_corners(crv=sel_list[0], name='round')




