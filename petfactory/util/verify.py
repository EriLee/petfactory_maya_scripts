import pymel.core as pm
#from inspect import isclass

def verify_pynode(node, node_type):
    
    '''Convert the string to a PyNode and check if it is an instance or subclass of the node_type argument.
    isinstance returns true if the object argument is an instance of the classinfo argument, or of a
    (direct, indirect or virtual) subclass thereof.
    '''
    # check if the node_type is a class
    #if not inspect.isclass(node_type):
    #    pm.warning('{0} is not a class'.format(node_type))
    #    return False
        
    # check if the node_type is valid
    if not pm.util.utilitytypes.ProxyUnicode in node_type.__mro__:
        pm.warning('{0} is not a valid node type'.format(node_type))
        return False
        
    # check if node is a valid PyNode
    if not isinstance(node, pm.util.utilitytypes.ProxyUnicode):
        pm.warning('{0} is not a PyNode'.format(node))
        return False
    
    # check if the node is an instance
    if isinstance(node, node_type):
        return True
    
    # if the node was not an instance, check the shape node
    else:
        
        try:
            shape = node.getShape()
                
        except AttributeError as e:
            #pm.warning('Select a transform to use the getShape method. {0}'.format(e))
            return False
            
        return isinstance(shape, node_type)

def verify_selection(node_type):
    
    '''Check if the first object in the selection list is an instance or subclass of the node_type argument.
    isinstance returns true if the object argument is an instance of the classinfo argument, or of a
    (direct, indirect or virtual) subclass thereof.
    
    usage:
        print(verify_selection(pm.nodetypes.NurbsCurve))
    '''
    # check if the node_type is valid
    if not pm.util.utilitytypes.ProxyUnicode in node_type.__mro__:
        pm.warning('{0} is not a valid node type'.format(node_type))
        return False

    sel = pm.ls(sl=True)
        
    if not sel:
        pm.warning('Nothing is selected!')
        
    # check if the node is an instance
    if isinstance(sel[0], node_type):
        return True
    
    # if the node was not an instance, check the shape node
    else:
        
        try:
            shape = sel[0].getShape()
                
        except AttributeError as e:
            #pm.warning('Select a transform to use the getShape method. {0}'.format(e))
            return False
            
        return isinstance(shape, node_type)


def verify_string(node_name, node_type):
    
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
              
    # check if the node is an instance
    if isinstance(node, node_type):
        return True
    
    # if the node was not an instance, check the shape node
    else:
        
        try:
            shape = node.getShape()
                
        except AttributeError as e:
            #pm.warning('Select a transform to use the getShape method. {0}'.format(e))
            return False
            
        return isinstance(shape, node_type)
        

def to_pynode(node_name):
    
    try:
        return(pm.PyNode(node_name))
        
    except pm.MayaNodeError as e:
        pm.warning('Could not create PyNode. {0}'.format(e))
        return None
