import pymel.core as pm

def add_vray_subdivision():

    sel_list = pm.ls(sl=True)
    
    for sel in sel_list:
        
        # do some checking here
        mesh = sel.getShape()
        
        if not isinstance(mesh, pm.nodetypes.Mesh):
            pm.warning('Not a polygon mesh, skipping')
            continue
            
        
        pm.vray("addAttributesFromGroup", mesh, "vray_subdivision", 1)
        pm.vray("addAttributesFromGroup", mesh, "vray_subquality", 1)
        
        
        try:
            mesh.vrayEdgeLength.set(1)
            mesh.vrayMaxSubdivs.set(16)
            
        except AttributeError as e:
            print e

            