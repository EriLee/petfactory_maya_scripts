import maya.OpenMaya as om
import pymel.core as pm
import math

#pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/locators.mb', f=True)


# create a plane
pos = [pm.PyNode('locator{0}'.format(n)).getTranslation(space='world') for n in range(4)]


numVertices = 4
numPolygons = 1

vertices = [om.MFloatPoint(p[0], p[1], p[2]) for p in pos]

vertexFloatPointArray = om.MFloatPointArray()

for vert in vertices:
    vertexFloatPointArray.append(vert)
    
    
count = [4]
polyCount = om.MIntArray()

for c in count:
    polyCount.append(int(c))


connection_list = [0,1,2,3]
polyConnections = om.MIntArray()

for connection in connection_list:
    polyConnections.append(int(connection))
  
meshFn = om.MFnMesh()
 
meshFn.create(numVertices, numPolygons, vertexFloatPointArray, polyCount, polyConnections)
