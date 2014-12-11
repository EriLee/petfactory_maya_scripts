import maya.OpenMaya as om
import pymel.core as pm
import math


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
        for p in profile_pos_list:
            pos_list.append(pm.datatypes.Vector(p.x, p.y+i, p.z))
            
    return pos_list
    
    
        
def create_poly_pipe(pos_list, axis_divisions, height_divisions, name):
    
    # total num verts
    numVertices = len(pos_list)
       
       
    # the total number of polygons in mesh
    numPolygons = axis_divisions * (height_divisions-1)
    
    
    # create the vertex array
    vertices = [om.MFloatPoint(p[0], p[1], p[2]) for p in pos_list]
    vertexFloatPointArray = om.MFloatPointArray()   
    for vert in vertices:
        vertexFloatPointArray.append(vert)
     
    
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
        
                          
    
    meshFn = om.MFnMesh()
    mesh = meshFn.create(numVertices, numPolygons, vertexFloatPointArray, polyCount, polyConnections)
    
    mesh_depend_node = om.MFnDependencyNode(mesh)
    mesh_depend_node.setName(name)
    return mesh_depend_node


axis_div = 12
height_div = 10
radius = 5

# create a profile list   
profile_pos_list = create_profile_points(radius=radius, axis_divisions=axis_div)
    
# create pos list
pos_list = create_pos_list(profile_pos_list=profile_pos_list, height_divisions=height_div)

# create the mesh
mesh = create_poly_pipe(pos_list=pos_list, axis_divisions=axis_div, height_divisions=height_div, name='myPipe')


print(mesh.name())
pm_mesh = pm.PyNode(mesh.name())
pm.select(pm_mesh)  

