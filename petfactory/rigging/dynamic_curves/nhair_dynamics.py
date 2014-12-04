def make_curve_dynamic(crv):
    
    pm.select(crv)
    
    scene_set_before = set(pm.ls())
    pm.mel.eval('MakeCurvesDynamic')
    scene_set_after = set(pm.ls())
    
    diff_set = scene_set_after.difference(scene_set_before)
    
    ret_dict = {}
    
    #pprint.pprint(diff_set)
    
    misc_list = [] 
    ret_dict['misc'] = misc_list
    
    for n in diff_set:
        
        if isinstance(n, pm.nodetypes.Transform):
            
            if isinstance(n.getShape(), pm.nodetypes.Follicle):
                ret_dict['follicle'] = n
                #print(n)
                
            elif isinstance(n.getShape(), pm.nodetypes.HairSystem):
                ret_dict['hairsystem'] = n
                #print(n)
                
            elif isinstance(n.getShape(), pm.nodetypes.NurbsCurve):
                #print(n)

                c = n.getParent()
                
                if c != crv:
                    ret_dict['output_curve'] = n
                              
            elif isinstance(n, pm.nodetypes.Nucleus):
                ret_dict['nucleus'] = n
                #print(n)
                
            else:
                #print(n)
                misc_list.append(n)

    return ret_dict