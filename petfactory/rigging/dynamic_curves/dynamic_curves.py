import pymel.core as pm
import maya.cmds as cmds
import pprint

#pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/crv.mb', force=True)
#crv_1 = pm.PyNode('crv_1')
#crv_2 = pm.PyNode('crv_2')
#dup_crv = pm.duplicate(crv)[0]


def make_dynamic(crv):
    
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
    


def make_curves_dynamic():
       
    follicle_grp = pm.group(em=True, name='follicle_grp')
    out_curve_grp = pm.group(em=True, name='output_curve_grp')

    del_list = []
    
    for index, sel in enumerate(sel_list):
        
       if index is 0:
           main_dynamic_dict = make_dynamic(sel)
           main_hairsystem = main_dynamic_dict['hairsystem']
           main_follicle = main_dynamic_dict['follicle']
           main_output_curve = main_dynamic_dict['output_curve']
           main_misc = main_dynamic_dict['misc']
           
           pm.setAttr('{}.pointLock'.format(main_follicle.getShape()), 1)
    
           
           pm.parent(main_follicle, follicle_grp)
           pm.parent(main_output_curve, out_curve_grp)
           
           
           del_list += main_misc
           
       else:
           dynamic_dict = make_dynamic(sel)
           hairsystem = dynamic_dict['hairsystem']
           follicle = dynamic_dict['follicle']
           output_curve = dynamic_dict['output_curve']
           misc = dynamic_dict['misc']
           
           pm.setAttr('{}.pointLock'.format(follicle.getShape()), 1)
           
           pm.parent(follicle, follicle_grp)
           pm.parent(output_curve, out_curve_grp)
           
           # connect follicle 2 to hairsystem1
           follicle.outHair >> main_hairsystem.inputHair[index]
           main_hairsystem.outputHair[index] >> follicle.currentPosition
           
           
           del_list += misc
           del_list.append(hairsystem)
           
    #pm.select(del_list, add=True)
    pm.delete(del_list)


'''
sel_list = pm.ls(sl=True)
if len(sel_list) < 1:
    pm.warning('Nothing is selected!')
else:
    make_curves_dynamic()
'''