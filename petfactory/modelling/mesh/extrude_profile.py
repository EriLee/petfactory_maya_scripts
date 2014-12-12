import maya.OpenMaya as om
import pymel.core as pm
import math
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
    

def create_profile_points(radius, axis_divisions):
    '''Returns a list of positions (pm.datatypes.Vector) on a circle 
    around the origin, in the xz plane, i.e. y axis as normal'''
    
    ang_inc = (math.pi*2)/axis_divisions
    
    p_list = []
    
    for i in range(axis_divisions):
        u = math.cos(ang_inc*i)*radius
        v = math.sin(ang_inc*i)*radius
        p_list.append(pm.datatypes.Vector(u, 0, v))
    
    # reverse the positions to end up with normals
    # pointing in the right direction :)
    p_list.reverse()
    return p_list


def create_pos_list(profile_pos_list, height_divisions):
 
    # all the positions that makes up the cylinder in a flat list
    pos_list = []
    for i in range(height_divisions):
        temp_list = []
        for p in profile_pos_list:
            temp_list.append(pm.datatypes.Vector(p.x, p.y+i, p.z))
        pos_list.append(temp_list)
            
    return pos_list
    
    
profile_pos = create_profile_points(radius=2, axis_divisions=12)  
pos_list = create_pos_list(profile_pos_list=profile_pos, height_divisions=20)
    
          

mesh = mesh_from_pos_list(pos_list=pos_list, name='test')
pm.select(mesh.name())
             
             