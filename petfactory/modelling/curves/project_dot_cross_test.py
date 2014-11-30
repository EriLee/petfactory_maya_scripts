import pymel.core as pm
import math

def line(pos_list, name=''):
    return pm.curve(degree=1, p=pos_list, name=name)
    
def pos(x, y, z=0):
    sp = pm.polySphere(r=.1)[0]
    sp.translate.set((x, y, z))
    return sp
    

sel_all = pm.ls(type='transform')
for x in sel_all:
    if x.name() != 'crv':
        pm.delete(x)  
    
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
#o = (0,0,0)
#line([o, aim_vec])
#line([o, up_vec_ortho])

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


#build a transformation matrix to transform vectors 
# from world space to the rotated space
tm = pm.datatypes.TransformationMatrix(
[aim_vec[0],aim_vec[1],aim_vec[2],0],
[up_vec_ortho[0], up_vec_ortho[1], up_vec_ortho[2],0],
[abc_cross[0], abc_cross[1], abc_cross[2], 0],


[0,0,0,1])

vec_test = pm.datatypes.Vector(up_u, up_v, 0)
rot_v = vec_test.rotateBy(tm)
pos(rot_v.x, rot_v.y, rot_v.z)

vec_test_2 = pm.datatypes.Vector(aim_u, aim_v, 0)
rot_v_2 = vec_test_2.rotateBy(tm)
pos(rot_v_2.x, rot_v_2.y, rot_v_2.z)



# calculate the theta angle
theta_aim = math.atan2(aim_v, aim_u)
theta_up = math.atan2(up_v, up_u)

aim_line = line([(0,0,0),(5,0,0)], name='aim_vec')
aim_line.rotate.set(0,0,pm.util.degrees(theta_aim))
    
up_line = line([(0,0,0),(5,0,0)], name='up_vec')
up_line.rotate.set(0,0,pm.util.degrees(theta_up))



