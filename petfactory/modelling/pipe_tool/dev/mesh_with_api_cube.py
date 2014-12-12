import pprint
profile_pos_list = [pm.PyNode('locator{0}'.format(n)).getTranslation(space='world') for n in range(4)]
num_radius_seg = len(profile_pos_list)
num_length_seg = 10

pos_list = []
for i in range(num_length_seg):
    for p in profile_pos_list:
        pos_list.append(pm.datatypes.Vector(p.x, p.y+i, p.z))
        

# create a vert array
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


polyCount = om.MIntArray()
for c in range(count):
    polyCount.append(int(4))


#print(count)

'''
connection_list = [ 0,1,5,4,
                    1,2,6,5,
                    2,3,7,6,
                    3,0,4,7
                  ]
'''

connection_list_r = [   0,1,5,4,
                        1,2,6,5,
                        2,3,7,6,
                        3,0,4,7,
                        4,5,9,8,
                        5,6,10,9,
                        6,7,11,10,
                        7,4,8,11,
                  ]
                  

connection_list = []
for c in range(numVertices-num_radius_seg):
    r_inc = (c/num_radius_seg*num_radius_seg)
    con = (     c,
                ((c+1)%num_radius_seg)+r_inc,
                ((c+1)%num_radius_seg)+num_radius_seg+r_inc,
                c+num_radius_seg)
    #print(con)
    connection_list.extend(con)
    #print(c)

    
polyConnections = om.MIntArray()
for con in connection_list:
    polyConnections.append(int(con))
    
                      
#print(connection_list_r)
#print(connection_list)
meshFn = om.MFnMesh()
meshFn.create(numVertices, numPolygons, vertexFloatPointArray, polyCount, polyConnections)


