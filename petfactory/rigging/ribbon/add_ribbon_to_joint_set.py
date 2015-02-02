#pm.openFile('/Users/johan/Documents/Projects/python_dev/scenes/jnt_ref.mb', f=True)

import petfactory.rigging.ribbon.create_ribbon as create_ribbon



def create_ribbon_for_joint_set():
    
    width = 35
    depth = 1
    num_u_patches = 10
    num_follicles = 50
    
    sel_list = pm.ls(sl=True)
    
    for sel in sel_list:
        member_list = sel.members()
        member_list.sort()
        
        # build the ribbon surface
        ribbon = create_ribbon.build_ribbon(width=width, depth=depth, num_u_patches=num_u_patches)
        
        # add follicles
        follicle_dict = create_ribbon.add_follicles(nurbs_surface=ribbon, num_follicles=num_follicles)
        
        # add joint to the follicles
        create_ribbon.add_follicle_joints(follicle_dict.get('follicle_transform_list'))
        
        #skinMethod 0 : linear, 1 : dual quaternion
        # ignoreHierarchy : Disregard the place of the joints in the skeleton hierarchy
        pm.skinCluster(member_list, ribbon, skinMethod=1, ignoreHierarchy=True)
        
        