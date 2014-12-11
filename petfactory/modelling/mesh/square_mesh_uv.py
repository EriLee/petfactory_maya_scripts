import maya.OpenMaya as om
import maya.cmds as cmds



vertexArray = om.MFloatPointArray()
uArray = om.MFloatArray()
vArray = om.MFloatArray()

numVertices = 4
numPolygons = 1

vertices = [(0,0,0), (1,0,0), (1,1,0), (0,1,0)]
uvs = [(0,0), (1,0), (1,1), (0,1)]
conns = [0,1,2,3] 
pConnects = om.MIntArray()

for c in conns:
    pConnects.append(c)

pCounts = om.MIntArray()


for o in range(numPolygons):
    pCounts.append(4)
    
uvCounts = om.MIntArray() 
uvIds = om.MIntArray()

for i in range(0, len(vertices)):

    pt = om.MFloatPoint(vertices[i][0],vertices[i][1], vertices[i][2])
    vertexArray.append(pt)
    uArray.append(uvs[i][0])
    vArray.append(uvs[i][1])
    uvIds.append(i)


# normally to fill uVcounts with only 1 UV set , the faceVertId are the same as face vert connection array : here 3 vertices/UV
uvCounts = pCounts 

#Now create the mesh
#build components
mesh = om.MFnMesh()


meshMObj = mesh.create(numVertices, numPolygons, vertexArray, pCounts, pConnects, uArray, vArray) #<-- don't forget to add a parent owner

#defaultUVSetName = ''
#defaultUVSetName = mesh.currentUVSetName(-1)
#mesh.assignUVs( uvCounts,uvIds,	defaultUVSetName) #< even if uv a created you must assign them
mesh.assignUVs( uvCounts,uvIds)