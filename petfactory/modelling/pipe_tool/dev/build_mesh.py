import pymel.core as pm
import math

pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)

height = 5
pos_list = [ ((-1, n, -1), (-1, n, 1), (1, n, 1), (1, n, -1)) for n in range(height) ]


num_faces = len(pos_list[0])

for i, pos in enumerate(pos_list):

    if i < height-1:
        
        for j, p in enumerate(pos):
        
            if j < num_faces-1:
                
                p_list = [pos_list[i][j], pos_list[i][j+1], pos_list[i+1][j+1], pos_list[i+1][j]]
                
            else:
                p_list = [pos_list[i][j], pos_list[i][0], pos_list[i+1][0], pos_list[i+1][j]]
   
            polygon = pm.polyCreateFacet(p=p_list, name='face_{0}_{1}'.format(i, j))
            

            #visualize the vertices
            '''
            for count, x in enumerate(p_list):
                sp=pm.polySphere(r=.1, name='sphere_{0}'.format(count))[0]
                sp.translate.set(x)
            '''


#pprint.pprint(pos_list)
    
