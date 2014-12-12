import maya.OpenMaya as om
import maya.cmds as cmds


# total number of vertices
numVertices = 6

# the total number of polygon faces
numPolygons = 2

# the vert positions
vertices = [    (0,0,0), (1,0,0), (1,1,0), (0,1,0), 
                (2,0,0), (2,1,0) 
           ]

# the vert connections
conns = [   0,1,2,3,
            1,4,5,2
        ] 
        
# the uv positions
uv_coords = [ (0,0), (1,0), (1,1), (0,1),
        (2,0), (2,1)
    ]
  

# uv connections (which vert to assign uv to)
uv_ids = [  0,1,2,3,
            1,4,5,2
         ]



# the vert connections
pConnects = om.MIntArray()
for c in conns:
    pConnects.append(c)

# the vert count per face
pCounts = om.MIntArray()
for o in range(numPolygons):
    pCounts.append(4)

# the vert positions
vertexArray = om.MFloatPointArray()
for i in range(0, len(vertices)):
    pt = om.MFloatPoint(vertices[i][0],vertices[i][1], vertices[i][2])
    vertexArray.append(pt)
    


  
# the uv count per face
uvCounts = om.MIntArray() 
for o in range(numPolygons):
    uvCounts.append(4)
 
# create u and v position array   
uArray = om.MFloatArray()
vArray = om.MFloatArray()
for i in range(numVertices):
    uArray.append(uv_coords[i][0])
    vArray.append(uv_coords[i][1])

# uv ids (vert id)
uvIds = om.MIntArray()       
for c in uv_ids:
    uvIds.append(c)           




# create a mesh function set
meshFn = om.MFnMesh()
# create a mesh
mesh = meshFn.create(numVertices, numPolygons, vertexArray, pCounts, pConnects, uArray, vArray)
# assign the uvs
meshFn.assignUVs(uvCounts, uvIds)