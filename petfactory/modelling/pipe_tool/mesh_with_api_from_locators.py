import maya.OpenMaya as om
import pymel.core as pm
import math

#pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/locators.mb', f=True)
pos = [pm.PyNode('locator{0}'.format(n+1)).getTranslation(space='world') for n in range(4)]


numVertices = 4
numPolygons = 1

vertices = [om.MFloatPoint(p[0], p[1], p[2]) for p in pos]

vertexFloatPointArray = om.MFloatPointArray()

for vert in vertices:
    vertexFloatPointArray.append(vert)
    
    
    

    
'''



meshFn = om.MFnMesh()
mergeVertices = True
pointTolerance = 0.001

faceArray = om.MPointArray()
faceArray.setLength(3)

faceArray.set(vertices[0], 0)
faceArray.set(vertices[1], 1)
faceArray.set(vertices[2], 2)


meshFn.addPolygon(faceArray, mergeVertices, pointTolerance)
'''