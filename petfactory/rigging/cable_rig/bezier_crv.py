import petfactory.util.dev as dev


def create_bezier_cv_loc(crv):
    
    def create_vector_product(loc, crv_shape, cv_index):
        
        # get the pos of the cv
        pos = crv_shape.getCV(cv_index)
        
        # get the cv pos in the local space of the loc 
        local_pos = pos * tm.inverse()
        
        # use vector product node to get the local position in the loc space
        vec_prod = pm.createNode('vectorProduct')
        vec_prod.operation.set(4)
        vec_prod.input1.set((local_pos[0], local_pos[1], local_pos[2]))
        loc.worldMatrix[0] >> vec_prod.matrix

        # let the local pos drive the cobtrol point of the bezier crv
        vec_prod.output >> crv_shape.controlPoints[cv_index]
                
        
           
    crv_shape = crv.getShape()
    num_cvs = crv_shape.numCVs()
    
    for cv in range(num_cvs):
        
        # every third cv (0,3,6...)
        if not cv%3:

            pos = crv_shape.getCV(cv)
            
            # build matrix
            u = crv_shape.getParamAtPoint(pos)            
            normal = crv_shape.normal(u).normal()
            tangent = crv_shape.tangent(u).normal()
            cross = tangent.cross(normal)
            
            tm = pm.datatypes.Matrix(   [[tangent[0],tangent[1],tangent[2],0],
                                        [normal[0],normal[1],normal[2],0],
                                        [cross[0],cross[1],cross[2],0],
                                        [pos[0],pos[1],pos[2],1]])


            # create loc    
            loc = pm.spaceLocator()
            loc.setMatrix(tm)
            loc.translate >> crv_shape.controlPoints[cv]
            
            

            if cv == 0:
                
                create_vector_product(loc, crv_shape, cv+1)
                                
            elif cv == num_cvs-1:
                
                create_vector_product(loc, crv_shape, cv-1)
  
            else:
                
                create_vector_product(loc, crv_shape, cv-1)
                create_vector_product(loc, crv_shape, cv+1)
                

    # create a nurbs curve based of the bezier crv
    nurbs_curve = pm.createNode('nurbsCurve')
    crv_shape.worldSpace[0] >> nurbs_curve.create


#dev.del_transform()

crv = pm.PyNode('bezier1')
create_bezier_cv_loc(crv)
#dir(crv_shape)




        
        