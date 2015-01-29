import pymel.core as pm


def create_joints_from_bb(jnt_axis=0, jnt_num=10):

    sel_list = pm.ls(sl=True)

    if not sel_list:
        pm.warning('Nothing is selected')
        return

    #xmin ymin zmin xmax ymax zmax.
    bb = pm.xform(sel_list[0], q=True, bb=True, ws=True)
    
    bb_min, bb_max = bb[jnt_axis], bb[jnt_axis+3]
    x_mid = (bb[3] - bb[0])*.5 + bb[0]
    y_mid = (bb[4] - bb[1])*.5 + bb[1]
    z_mid = (bb[5] - bb[2])*.5 + bb[2]
    
    dist = bb_max - bb_min
    jnt_spacing = dist / (jnt_num-1)
    
    
    for x in xrange(jnt_num):
        
        if jnt_axis is 0:
            trans = [(bb_min+jnt_spacing*x), y_mid, z_mid]
            
        elif jnt_axis is 1:
            trans = [x_mid, (bb_min+jnt_spacing*x), z_mid]
            
        else:
            trans = [x_mid, y_mid, (bb_min+jnt_spacing*x)]
      
        jnt = pm.createNode('joint', ss=True)
        jnt.translate.set(trans)

