import pymel.core as pm
import math


pos_list = [(0,1), (.2,1), (.2, 1.3), (.5, 1.3), (.5, 0)]

crv = None
for pos in pos_list:
    
    if crv is None:
        crv = pm.curve(d=1, p=[(pos[0], pos[1], 0)])
        print(crv)
        
    else:
        pass
        #pm.curve.(crv, append=True, p=[(pos[0], pos[1], 0)])
        pm.curve(crv, a=True, p=[(pos[0], pos[1], 0)] )
