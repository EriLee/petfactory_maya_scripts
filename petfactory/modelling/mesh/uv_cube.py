import maya.OpenMaya as om
import pymel.core as pm

axis_div = 4
height_div = 3


# the vert positions
pos_list = [ [-1.0, 0.0, -1.0],
             [-1.0, 0.0, 1.0],
             [1.0, 0.0, 1.0],
             [1.0, 0.0, -1.0],
             [-1.0, 2.0, -1.0],
             [-1.0, 2.0, 1.0],
             [1.0, 2.0, 1.0],
             [1.0, 2.0, -1.0],
             [-1.0, 4.0, -1.0],
             [-1.0, 4.0, 1.0],
             [1.0, 4.0, 1.0],
             [1.0, 4.0, -1.0]] 


# total number of vertices
numVertices = len(pos_list)

# the total number of polygon faces
numPolygons = 8

# the poly conections
connection_list = [ 0,1,5,4,
                    1,2,6,5,
                    2,3,7,6,
                    3,0,4,7,
                    4,5,9,8,
                    5,6,10,9,
                    6,7,11,10,
                    7,4,8,11
                    
                    
                  ]

# the uv positions
'''
uv_coords = [   (0,0), (1,0), (2,0), (3,0), (4,0),
                (0,1), (1,1), (2,1), (3,1), (4,1),
                (0,2), (1,2), (2,2), (3,2), (4,2)
            ]
'''

uv_coords = []
for v in range(height_div):
    for u in range(axis_div+1):
        uv_coords.append((u, v))
        
    


# uv connections (which vert to assign uv to)
uv_ids = []
for n in range(numPolygons):
    
    o = n/axis_div
    a = (
    
        n+o, n+1+o, n+2+axis_div+o, n+1+axis_div+o

    )
    uv_ids.extend(a)

print(uv_ids)


polyConnections = om.MIntArray()
for con in connection_list:
    polyConnections.append(con)

# the vert count per face
polyCount = om.MIntArray()
for o in range(numPolygons):
    polyCount.append(4)

# the vert positions
vertexArray = om.MFloatPointArray()
for pos in pos_list:
    pt = om.MFloatPoint(pos[0], pos[1], pos[2])
    vertexArray.append(pt)
    

# the uv count per face
uvCounts = om.MIntArray()
for o in range(numPolygons):
    uvCounts.append(4)

# create u and v position array   
uArray = om.MFloatArray()
vArray = om.MFloatArray()

for i in range(len(uv_coords)):
    uArray.append(uv_coords[i][0])
    vArray.append(uv_coords[i][1])

# uv ids (vert id)
uvIds = om.MIntArray()       
for c in uv_ids:
    print(c)
    uvIds.append(c)           


# create a mesh function set
meshFn = om.MFnMesh()
# create a mesh
#mesh = meshFn.create(numVertices, numPolygons, vertexArray, polyCount, polyConnections)
mesh = meshFn.create(numVertices, numPolygons, vertexArray, polyCount, polyConnections, uArray, vArray)
# assign the uvs
meshFn.assignUVs(uvCounts, uvIds)

mesh_depend_node = om.MFnDependencyNode(mesh)
pm.select(mesh_depend_node.name())

