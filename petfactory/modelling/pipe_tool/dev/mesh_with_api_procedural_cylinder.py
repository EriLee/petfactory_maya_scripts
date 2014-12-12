import maya.OpenMaya as om
import pymel.core as pm
import math


def create_profile_points(radius, num_points):
    '''Returns a list of positions (pm.datatypes.Vector) on a circle 
    around the origin, in the xz plane, i.e. y axis as normal'''
    
    ang_inc = (math.pi*2)/num_points
    
    p_list = []
    
    for i in range(num_points):
        u = math.cos(ang_inc*i)*radius
        v = math.sin(ang_inc*i)*radius
        p_list.append(pm.datatypes.Vector(u, 0, v))
    
    # reverse the positions to end up with normals
    # pointing in the right direction :)
    p_list.reverse()
    return p_list



# create a profile list   
profile_pos_list = create_profile_points(2, 12)
  
# the number of radius subdivisions / segments  
num_radius_seg = len(profile_pos_list)

# the number of length segments
num_length_seg = 10


# all the positions that makes up the cylinder in a flat list
pos_list = []
for i in range(num_length_seg):
    for p in profile_pos_list:
        pos_list.append(pm.datatypes.Vector(p.x, p.y+i, p.z))




        
# create the vertex array
vertices = [om.MFloatPoint(p[0], p[1], p[2]) for p in pos_list]
vertexFloatPointArray = om.MFloatPointArray()

for vert in vertices:
    vertexFloatPointArray.append(vert)

    
# total vert count
numVertices = len(pos_list)



# the total number of polygons in mesh
numPolygons = num_radius_seg * (num_length_seg-1)



# the total number of polygons
count = num_radius_seg * (num_length_seg-1)


# the number of verts per face
polyCount = om.MIntArray()
for c in range(count):
    polyCount.append(int(4))



# create the connection list
connection_list = []
for c in range(numVertices-num_radius_seg):
    r_inc = (c/num_radius_seg*num_radius_seg)
    con = (     c,
                ((c+1)%num_radius_seg)+r_inc,
                ((c+1)%num_radius_seg)+num_radius_seg+r_inc,
                c+num_radius_seg)
    connection_list.extend(con)

    
polyConnections = om.MIntArray()
for con in connection_list:
    polyConnections.append(int(con))
    
                      

meshFn = om.MFnMesh()
mesh = meshFn.create(numVertices, numPolygons, vertexFloatPointArray, polyCount, polyConnections)

mesh_depen_node = om.MFnDependencyNode(mesh)
print(mesh_depen_node.name())

mesh_depen_node.setName('pipe')

mesh_name = mesh_depen_node.name()
print(mesh_name)

pm_mesh = pm.PyNode(mesh_name)

pm.select(pm_mesh)
