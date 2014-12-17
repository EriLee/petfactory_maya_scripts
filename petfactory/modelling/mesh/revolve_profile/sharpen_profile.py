import pymel.core as pm
import math


def draw_crv_from_pos_list(pos_list):
    
    crv = None
    for pos in pos_list:
        
        if crv is None:
            crv = pm.curve(d=1, p=[(pos[0], pos[1], 0)])
            print(crv)
            
        else:
            pass
            #pm.curve.(crv, append=True, p=[(pos[0], pos[1], 0)])
            pm.curve(crv, a=True, p=[(pos[0], pos[1], 0)] )


pos_list = [pm.datatypes.Vector(p[0], p[1], 0) for p in [(0,1), (.2,1), (.2, 1.3), (.5, 1.3), (.5, 0)]]

sharpen_size = .02
num_pos = len(pos_list)
sharpen_pos_list = []

for index, pos in enumerate(pos_list):
    
    if index is not 0 and index is not num_pos-1:
        
        sharpen_back_pos = pos + (pos_list[index-1] - pos_list[index]).normal() * sharpen_size
        sharpen_forw_pos = pos + (pos_list[index+1] - pos_list[index]).normal() * sharpen_size
        
        sharpen_pos_list.extend([sharpen_back_pos, pos, sharpen_forw_pos])
        
    
    else:
        sharpen_pos_list.append(pos)




#draw_crv_from_pos_list(pos_list=sharpen_pos_list)