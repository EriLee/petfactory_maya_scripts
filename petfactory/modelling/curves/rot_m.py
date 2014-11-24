import pymel.core as pm
'''
m = [  [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1],
]
'''

m = pm.ls(sl=True)[0].getMatrix()
tm = pm.datatypes.TransformationMatrix(m)

vec = pm.datatypes.Vector(1,0,0);

vec_rot = vec.rotateBy(tm)

loc = pm.spaceLocator()
loc.translate.set(vec_rot)

