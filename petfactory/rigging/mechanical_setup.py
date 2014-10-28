import pymel.core as pm

def get_radius(node):
    history = pm.listHistory(node, future=False, pruneDagObjects=True)[0]
    return history.radius.get()


def connect_cogs(obj_list, radius_list=None):
    
    for index, obj in enumerate(obj_list):
        
        if index is not 0:
            
            source = obj_list[index-1]
            
            if radius_list is None:
                source_radius = get_radius(source)
                obj_radius = get_radius(obj)
                
            else:
                source_radius = float(radius_list[index-1])
                obj_radius = float(radius_list[index])
            
            factor = source_radius/obj_radius 
            print(factor)
            md = pm.createNode('multDoubleLinear', name='cog_mdl')
            source.ry >> md.input1
            md.input2.set(-factor)
            md.output >> obj.ry

        
sel_list = pm.ls(sl=True)
connect_cogs(sel_list, radius_list=[3,2,1,4,2,1,1])

