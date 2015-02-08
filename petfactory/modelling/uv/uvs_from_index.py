import pprint
import random
import petfactory.util.dev as dev

# delete transforms
dev.del_transform()

num_items_internal_u = 2
num_items_internal_v = 2
num_items_internal_patch = num_items_internal_u * num_items_internal_v
max_patches_u = 10


def uv_from_index_list(uv_num, start_index=0, num_random=None):
    
    uv_list = []
    for index in range(start_index, (uv_num+start_index)):
        
        # if num_random is specified (int) set the index to be a random
        # number between start_index -> start_index + num_random
        if num_random is not None:
            index = start_index + random.randint(0, (num_random-1))
            
        # internal uv
        internal_u = (index % num_items_internal_u) / float(num_items_internal_u)
        internal_v = ((index / num_items_internal_u) % num_items_internal_v) / float(num_items_internal_v)
        
        # patch index
        patch_index_u = (index / num_items_internal_patch) % max_patches_u
        patch_index_v = index / (num_items_internal_patch * max_patches_u)
        
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
    

uv_list = uv_from_index_list(uv_num=40, start_index=4, num_random=8)
#pprint.pprint(uv_list)

for index, uv in enumerate(uv_list):
    plane = pm.polyPlane(n='index_{0}'.format(index), axis=(0,0,1), h=1.0/num_items_internal_u, w=1.0/num_items_internal_v, sw=1, sh=1)[0]
    plane.translate.set(uv[0], uv[1], 0
    
#uv_from_index(191)
    
    
    