import maya.OpenMaya as om


# create a polygon face
pos = [(-1, 0, 0), (1, 0, 0), (0, 1, 0)]

vertices = [om.MPoint(p[0], p[1], p[2]) for p in pos]

meshFn = om.MFnMesh()
mergeVertices = True
pointTolerance = 0.001

faceArray = om.MPointArray()
faceArray.setLength(3)

faceArray.set(vertices[0], 0)
faceArray.set(vertices[1], 1)
faceArray.set(vertices[2], 2)


meshFn.addPolygon(faceArray, mergeVertices, pointTolerance)