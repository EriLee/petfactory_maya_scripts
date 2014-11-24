import pymel.core as pm

'''
m_1 = [  [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1],
]
'''

m_1 = pm.ls(sl=True)[0].getMatrix(worldSpace=True)
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

