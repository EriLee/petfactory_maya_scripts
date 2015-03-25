import pymel.core as pm

import petfactory.util.verify as pet_verify

def del_transform(exclude_list=[]):
    
    ''' delets all transforms in the scene, except for the cameras. Additional nodes can be
    excluded by adding the node type to be excluded to the exclude list
    
    usage:
        del_transform(exclude_list=[pm.nodetypes.Joint])'''
    
    exclude_list.append(pm.nodetypes.Camera)    
    t_list = pm.ls(type='transform')    
    del_list = [ t for t in t_list if pet_verify.get_nodetype(t) not in exclude_list]
    pm.delete(del_list)


color_dict = {  "black":1,
                "blue":6,
                "red":13,
                "green":14,
                "white":16,
                "yellow":17}

    
def line(e, s=(0,0,0), c=None):
    
    crv = pm.curve(d=1, p=[s, e])
    crv_shape = crv.getShape()
    
    color = color_dict.get(c) 
    if c is not None and color is not None:
        crv_shape.overrideEnabled.set(1)
        crv_shape.overrideColor.set(color)

    pm.select(deselect=True)

def point(p, r=.25, c=None):
    
    sp = pm.createNode('renderSphere')
    sp.getParent().translate.set(p)
    sp.radius.set(r)
    
    color = color_dict.get(c) 
    if c is not None and color is not None:
        sp.overrideEnabled.set(1)
        sp.overrideColor.set(color)

    pm.select(deselect=True)
