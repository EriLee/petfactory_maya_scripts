import maya.OpenMaya as om
import pymel.core as pm
import pprint

def mesh_from_pos_list(pos_list, name):

    height_divisions = len(pos_list)
    axis_divisions = len(pos_list[0])
    

    if height_divisions < 2:
        pm.warning('height_divisions must be at least 2!')
        return

    if axis_divisions < 2:
        pm.warning('axis_divisions must be at least 2!')
        return

    
    # total num verts
    numVertices = height_divisions * axis_divisions
       
       
    # the total number of polygons in mesh
    numPolygons = axis_divisions * (height_divisions-1)
    
    
    # create the vertex array
    vertexFloatPointArray = om.MFloatPointArray()  
    for axis_pos in pos_list:
        for pos in axis_pos:
            vertexFloatPointArray.append(om.MFloatPoint(pos[0], pos[1], pos[2]))

    
    # the number of verts per face
    polyCount = om.MIntArray()
    for c in range(numPolygons):
        polyCount.append(int(4))
       
    
    # create the connection list
    connection_list = []
    for c in range(numVertices-axis_divisions):
 
        r_inc = (c/axis_divisions*axis_divisions)
        
        con = ( c,
                ((c+1)%axis_divisions)+r_inc,
                ((c+1)%axis_divisions)+axis_divisions+r_inc,
                c+axis_divisions)
                
        connection_list.extend(con)
    
        
    polyConnections = om.MIntArray()
    for con in connection_list:
        polyConnections.append(int(con))
        

    # uv connections (which vert to assign uv to)  
    # the uv count per face
    uvCounts = om.MIntArray()
    for o in range(numPolygons):
        uvCounts.append(int(4))
    
 
    
    uv_ids = []
    for n in range(numPolygons):
        
        o = n/axis_divisions
        a = (
        
            n+o, n+1+o, n+2+axis_divisions+o, n+1+axis_divisions+o
    
        )
        uv_ids.extend(a)
    
    
    
    
    uv_coords = []
    for v in range(height_divisions):
        for u in range(axis_divisions+1):
            uv_coords.append((u, v))
            

    
    # create u and v position array   
    uArray = om.MFloatArray()
    vArray = om.MFloatArray()
    
    for i in range(len(uv_coords)):
        uArray.append(uv_coords[i][0])
        vArray.append(uv_coords[i][1])
    
    # uv ids (vert id)
    uvIds = om.MIntArray()       
    for c in uv_ids:
        uvIds.append(c)           

                      
    
    meshFn = om.MFnMesh()
    mesh = meshFn.create(numVertices, numPolygons, vertexFloatPointArray, polyCount, polyConnections, uArray, vArray)
    # assign the uvs
    meshFn.assignUVs(uvCounts, uvIds)
    
    mesh_depend_node = om.MFnDependencyNode(mesh)
    mesh_depend_node.setName(name)
    return mesh_depend_node
    


pos_list = [ [   [-1.0, 0.0, -1.0],
                 [-1.0, 0.0, 1.0],
                 [1.0, 0.0, 1.0],
                 [1.0, 0.0, -1.0]
                 ],
                 
             [   [-1.0, 2.0, -1.0],
                 [-1.0, 2.0, 1.0],
                 [1.0, 2.0, 1.0],
                 [1.0, 2.0, -1.0]
                 ],
                 
             [
                 [-1.0, 4.0, -1.0],
                 [-1.0, 4.0, 1.0],
                 [1.0, 4.0, 1.0],
                 [1.0, 4.0, -1.0]
                 ],
                 
             [   [-1.0, 6.0, -1.0],
                 [-1.0, 6.0, 1.0],
                 [1.0, 6.0, 1.0],
                 [1.0, 6.0, -1.0]]
                 ] 
#pprint.pprint(pos_list)            

mesh = mesh_from_pos_list(pos_list=pos_list, name='test')
pm.select(mesh.name())
             
             