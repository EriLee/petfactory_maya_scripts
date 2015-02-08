import pprint
import random
import petfactory.util.dev as dev

'''
Let the user worry about the padding etc?
just tile the number of specified shells?

add a pre estimate number of shells in u and v?
and margin estimate.

'''


# delete transforms
dev.del_transform()

def uv_from_index_list(num_items_u, num_items_v, num_items, start_index=0, num_random=None):
    
    num_items_per_patch = num_items_u * num_items_v
    max_patches_u = 10

    uv_dict = {}
    for index in range(start_index, (num_items + start_index)):
        
        # if num_random is specified (int) set the index to be a random
        # number between start_index -> start_index + num_random
        if num_random is not None:
            index = start_index + random.randint(0, (num_random-1))
            
        # internal uv
        local_u = (index % num_items_u) / float(num_items_u)
        local_v = ((index / num_items_u) % num_items_v) / float(num_items_v)
        
        # patch index
        patch_index_u = (index / num_items_per_patch) % max_patches_u
        patch_index_v = index / (num_items_per_patch * max_patches_u)
        
        u = patch_index_u + local_u
        v = patch_index_v + local_v
                
        udim = 1000 + (patch_index_u + 1) + (max_patches_u * patch_index_v)

        # create a key in the dict using the udim
        if udim not in uv_dict:
            uv_dict[udim] = []

        uv_dict[udim].append((u,v))
                
    return uv_dict


'''
def uv_from_index(n):
    
    internal_u = (n % num_items_internal_u) / float(num_items_internal_u)
    internal_v = ((n / num_items_internal_u) % num_items_internal_v) / float(num_items_internal_v)
    
    patch_index_u = (n / num_items_internal_patch) % max_patches_u
    patch_index_v = n / (num_items_internal_patch * max_patches_u)
    
    u = patch_index_u + internal_u
    v = patch_index_v + internal_v
    
    plane = pm.polyPlane(n='NEW_index_{0}'.format(n), axis=(0,0,1), h=1.0/num_items_internal_u, w=1.0/num_items_internal_v, sw=1, sh=1)[0]
    plane.translate.set(u, v, 0)
'''
    
num_items_u = 2
num_items_v = 2
num_items = 40
start_index = 8
num_random = None

uv_dict = uv_from_index_list(num_items_u=num_items_u, num_items_v=num_items_v, num_items=num_items, start_index=start_index, num_random=num_random)
#pprint.pprint(uv_dict)


for udim, uv_list in uv_dict.iteritems():
    
    for uv in uv_list:
        plane = pm.polyPlane(n='UDIM_{0}_{1}{2}'.format(udim, uv[0], uv[1]), axis=(0,0,1), h=1.0/num_items_v, w=1.0/num_items_u, sw=1, sh=1)[0]
        plane.translate.set(uv[0], uv[1], 0)
    

#uv_from_index(191)
    
    
    