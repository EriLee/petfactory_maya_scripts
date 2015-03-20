import pymel.core as pm

def verify_selection(node_type, use_shape=False):
    
    '''Check if the first object in the selection list is an instance or subclass of the node_type argument.
    isinstance returns true if the object argument is an instance of the classinfo argument, or of a
    (direct, indirect or virtual) subclass thereof.
    
    usage:
        print(verify_selection(pm.nodetypes.NurbsCurve, True))
    '''
    
    sel = pm.ls(sl=True)
        
    if not sel:
        pm.warning('Nothing is selected!')
        
    if use_shape:
        
        try:
            shape = sel[0].getShape()
                
        except AttributeError as e:
            pm.warning('Select a transform to use the getShape method. {0}'.format(e))
            return False
            
        return isinstance(shape, node_type)
            
    else:                 
        return isinstance(sel[0], node_type)


def verify_string(node_name, node_type, use_shape=False):
    
    '''Convert the string to a PyNode and check if it is an instance or subclass of the node_type argument.
    isinstance returns true if the object argument is an instance of the classinfo argument, or of a
    (direct, indirect or virtual) subclass thereof.
    
    usage:
        print(verify_string('curve1', pm.nodetypes.Transform, False))
    '''
    
    try:
        node = pm.PyNode(node_name)
        
    except pm.MayaNodeError as e:
        pm.warning('Could not create PyNode, {0}'.format(e))
        return False
              
    if use_shape:
        
        try:
            shape = node.getShape()
                
        except AttributeError as e:
            pm.warning('Select a transform to use the getShape method. {0}'.format(e))
            return False
            
        return isinstance(shape, node_type)
            
    else:                 
        return isinstance(node, node_type)

def to_pynode(node_name):
    
    try:
        return(pm.PyNode(node_name))
        
    
    except pm.MayaNodeError as e:
        pm.warning('Could not create PyNode. {0}'.format(e))
        return None
