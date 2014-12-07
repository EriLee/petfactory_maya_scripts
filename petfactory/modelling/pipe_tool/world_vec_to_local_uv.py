#pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)
pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/empty_scene.mb', f=True)

def loc(p, size=.2):
    loc = pm.spaceLocator()
    loc.localScale.set((size,size,size))
    loc.translate.set(p)


crv = pm.curve(d=1, p=[(10,2,0), (7, 3, 0), (10, 5, 0)])

cv_list = crv.getCVs()

vec_aim = pm.datatypes.Vector(cv_list[0] - cv_list[1]).normal()
vec_up = pm.datatypes.Vector(cv_list[2] - cv_list[1]).normal()
pos = pm.datatypes.Vector(cv_list[1])

# construct a orthogonalized coordinate space
vec_cross = vec_aim.cross(vec_up).normal()
vec_up_ortho = vec_cross.cross(vec_aim).normal()

# create a transformation matrix
tm = pm.datatypes.TransformationMatrix( [ [vec_aim.x, vec_aim.y, vec_aim.z, 0],
                                          [vec_up_ortho.x, vec_up_ortho.y, vec_up_ortho.z, 0],   
                                          [vec_cross.x, vec_cross.y, vec_cross.z, 0],   
                                          [pos.x, pos.y, pos.z, 1] 
                                            
                                        ])
# bring the 3d pos to 2d uv space, by using the dot product to project on the orthogonal "base vectors"
aim_u = vec_aim.dot(vec_aim)
aim_v = vec_aim.dot(vec_up_ortho)

up_u = vec_up.dot(vec_aim)
up_v = vec_up.dot(vec_up_ortho)

theta = math.atan2(up_v, up_u)

radius = 2



# visulaize

#print(pm.util.degrees(theta))
#loc((aim_u, aim_v, 0))
#loc((up_u, up_v, 0))


#loc(vec_ba)
#loc(vec_bc)

#cube = pm.polyCube()[0]
#cube.setMatrix(tm)
