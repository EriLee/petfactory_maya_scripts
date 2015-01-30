def build_ribbon(num_joints=10):
    
    plane_u_patches = num_joints - 1
    plane_length_ratio = 1.0 / plane_u_patches
    plane_pivot_pos = plane_u_patches*.5,0,0
    
    ribbon_plane = pm.nurbsPlane(ax=(0,1,0), n='ribbon_geo', ch=False, patchesU=plane_u_patches, width=plane_u_patches, lengthRatio=plane_length_ratio, pivot=plane_pivot_pos)

    return ribbon_plane[0]
    
def add_follicles(nurbs_surface, num_follicles=10, direction='u', name='ribbon'):
    
    # chack that the user has provided:
    # a NurbsSurface
    # that the direction is valid 'u' or 'v'
    
    
    # max u, min u, max v, min v
    min_u, max_u, min_v, max_v = nurbs_surface.getKnotDomain()

    if direction == 'u':
        uv_inc = max_u / (num_follicles-1)
        
    if direction == 'v':
        uv_inc = max_v / (num_follicles-1)
  
    follicle_grp = pm.group(em=True, n='{0}_follicle_grp'.format(name))
    
    ret_dict = {}
    follicle_list = []
    ret_dict['follicle_grp'] = follicle_grp
    ret_dict['follicle_list'] = follicle_list
        
    
    for n in range(num_follicles):
    
        follicle_shape = pm.createNode('follicle', ss=1, n='{0}_FollicleShape_{1}'.format(name, n))
        follicle_transform = follicle_shape.getParent()
        follicle_list.append(follicle_shape)
        
        follicle_shape.outRotate >> follicle_transform.rotate
        follicle_shape.outTranslate >> follicle_transform.translate
        
        nurbs_surface.local >> follicle_shape.inputSurface
        nurbs_surface.worldMatrix[0] >> follicle_shape.inputWorldMatrix

        if direction == 'u':
            follicle_shape.parameterU.set(n * uv_inc)
            follicle_shape.parameterV.set(.5)
            
        if direction == 'v':
            follicle_shape.parameterU.set(.5)
            follicle_shape.parameterV.set(n * uv_inc)
            
        pm.parent(follicle_transform, follicle_grp)
    
    return ret_dict
            


# build the ribbon surface
ribbon = build_ribbon(num_joints=10)

follicle_dict = add_follicles(nurbs_surface=ribbon, num_follicles=50)
#print(follicle_dict.get('follicle_list'))