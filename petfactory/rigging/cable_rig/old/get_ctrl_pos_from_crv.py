import pymel.core as pm


pm.openFile('/Users/johan/Documents/Projects/python_dev/scenes/3deg_crv.mb', f=True)



def get_ctrl_pos_from_crv(crv):
        
    crv_shape = crv.getShape()
    crv_cvs = crv.getCVs(space='world')
    crv_num_cvs = len(crv_cvs)
        
    up_axis = pm.datatypes.Vector(0,1,0)
    
    start_cv_0 = crv_cvs[0]
    start_cv_1 = crv_cvs[1]
    
    start_aim = (start_cv_1 - start_cv_0).normal()
    start_cross = start_aim.cross(up_axis).normal()
    start_ortho_up = start_cross.cross(start_aim).normal()
    
    start_tm = pm.datatypes.TransformationMatrix(   [start_aim[0], start_aim[1], start_aim[2], 0], 
                                                    [start_ortho_up[0], start_ortho_up[1], start_ortho_up[2], 0],
                                                    [start_cross[0], start_cross[1], start_cross[2], 0],
                                                    [start_cv_0[0], start_cv_0[1], start_cv_0[2], 1])
    
    
    
    
    end_cv_0 = crv_cvs[-2]
    end_cv_1 = crv_cvs[-1]
    
    end_aim = (end_cv_1 - end_cv_0).normal()
    end_cross = end_aim.cross(up_axis).normal()
    end_ortho_up = end_cross.cross(end_aim).normal()
    
    end_tm = pm.datatypes.TransformationMatrix( [end_aim[0], end_aim[1], end_aim[2], 0], 
                                                [end_ortho_up[0], end_ortho_up[1], end_ortho_up[2], 0],
                                                [end_cross[0], end_cross[1], end_cross[2], 0],
                                                [end_cv_1[0], end_cv_1[1], end_cv_1[2], 1])
                                            
                                            
    return [start_tm, end_tm]                            


start_ctrl = pm.circle(name='start_ctrl', normal=(1,0,0))[0]
end_ctrl = pm.circle(name='end_ctrl', normal=(1,0,0))[0]
crv = pm.PyNode('curve1')
   
ctrl_pos_list = get_ctrl_pos_from_crv(crv)
start_ctrl.setMatrix(ctrl_pos_list[0])
end_ctrl.setMatrix(ctrl_pos_list[1])


