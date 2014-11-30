import pymel.core as pm
import math

def line(pos_list):
    pm.curve(degree=1, p=pos_list)
    
def pos(x, y):
    sp = pm.polySphere(r=.1)[0]
    sp.translate.set((x, y, 0))
    
# get the curve
crv = pm.PyNode('crv')
# get the cv positions
pos_list = crv.getShape().getCVs(space='world')

# define the vectors
ba_vec = pos_list[0] - pos_list[1]
bc_vec = pos_list[2] - pos_list[1]

# normalize
aim_vec = ba_vec.normal()
up_vec = bc_vec.normal()

# get the cross
abc_cross = ba_vec.cross(bc_vec).normal()

# make sure the up vector is orthogonal
up_vec_ortho = abc_cross.cross(aim_vec)

# visualize the ortho vectors
o = (0,0,0)
line([o, aim_vec])
line([o, up_vec_ortho])

# "project" the vector on the ortogonal vectors using the dot product
# i.e. find out how much the vector points in the same direction as the
# orthogonal vector
up_u = up_vec.dot(aim_vec)
up_v = up_vec.dot(up_vec_ortho)

aim_u = aim_vec.dot(aim_vec)
aim_v = aim_vec.dot(up_vec_ortho)

# visualize the uv pos
pos(up_u, up_v)
pos(aim_u, aim_v)
    



