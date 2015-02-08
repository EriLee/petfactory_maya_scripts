import pprint

num_items_internal_u = 2
num_items_internal_v = 2
num_items_internal_patch = num_items_internal_u * num_items_internal_v
max_patches_u = 10


def tile_uvs(sel_num):
    
    uv_list = []
    for n in range(sel_num):
        
        # internal uv
    	internal_u = (n % num_items_internal_u) / float(num_items_internal_u)
    	internal_v = ((n / num_items_internal_u) % num_items_internal_v) / float(num_items_internal_v)
    	
    	# patch index
    	patch_index_u = (n / num_items_internal_patch) % max_patches_u
    	patch_index_v = n / (num_items_internal_patch * max_patches_u)
    	
    	u = patch_index_u + internal_u
    	v = patch_index_v + internal_v
    	    	
    	uv_list.append((u,v))    	
    
    return uv_list


def uv_from_index(n):
    
    internal_u = (n % num_items_internal_u) / float(num_items_internal_u)
    internal_v = ((n / num_items_internal_u) % num_items_internal_v) / float(num_items_internal_v)
    
    patch_index_u = (n / num_items_internal_patch) % max_patches_u
    patch_index_v = n / (num_items_internal_patch * max_patches_u)
    
    u = patch_index_u + internal_u
    v = patch_index_v + internal_v
    
    plane = pm.polyPlane(n='NEW_index_{0}'.format(n), axis=(0,0,1), h=1.0/num_items_internal_u, w=1.0/num_items_internal_v, sw=1, sh=1)[0]
    plane.translate.set(u, v, 0)
	

sel_num = 100
uv_list = tile_uvs(sel_num)
pprint.pprint(uv_list)

for index, uv in enumerate(uv_list):
    plane = pm.polyPlane(n='index_{0}'.format(index), axis=(0,0,1), h=1.0/num_items_internal_u, w=1.0/num_items_internal_v, sw=1, sh=1)[0]
    plane.translate.set(uv[0], uv[1], 0)
#uv_from_index(191)
	
    
    