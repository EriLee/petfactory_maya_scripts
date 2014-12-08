import pymel.core as pm

sel = pm.ls(sl=True)[0]

crv_shape = sel.getShape()

#dir(crv_shape)
degree = crv_shape.degree()
num_cvs = crv_shape.numCVs()
arc_length = pm.arclen(crv_shape)



