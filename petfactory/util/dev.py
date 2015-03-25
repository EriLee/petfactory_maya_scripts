import pymel.core as pm

def del_transform():
	t_list = pm.ls(type='transform')
	del_list = [ x for x in t_list if not isinstance(x.getShape(), pm.nodetypes.Camera)]
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
    

#line((10,10,10), c='yellow')
#point((10,10,10), c='yellow')
