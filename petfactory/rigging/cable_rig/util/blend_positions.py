pm.openFile('/Users/johan/Documents/Projects/python_dev/scenes/empty_scene.mb', f=True)
ctrl = pm.circle(ch=False)[0]
crv = pm.curve(d=3, ep=[(0,0,0), (5,5,0)])
crv_shape = crv.getShape()



# use a vector product node to get a local position to world position
vector_prod = pm.createNode('vectorProduct')
# set to point matrix product
vector_prod.operation.set(4)
# set the position
vector_prod.input1Y.set(5)
ctrl.worldMatrix[0] >> vector_prod.matrix



# create a pointOncrvinfo to get a ws position from a curve param
point_on_crv = pm.createNode('pointOnCurveInfo')
# set which param to sample
point_on_crv.parameter.set(0.5)
point_on_crv.turnOnPercentage.set(1)
crv_shape.worldSpace[0] >> point_on_crv.inputCurve



# blend the positions
blend_col = pm.createNode('blendColors')
vector_prod.output >> blend_col.color1
point_on_crv.position >> blend_col.color2


# hook up the output
loc = pm.spaceLocator()
blend_col.output >> loc.translate

