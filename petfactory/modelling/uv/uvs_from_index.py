import random, math, pprint
import petfactory.util.dev as dev

'''
Let the user worry about the padding etc?
just tile the number of specified shells?

add a pre estimate number of shells in u and v?
and margin estimate.

'''


# delete transforms
dev.del_transform()

def udim_from_index(num_items_u, num_items_v, num_items, start_index=0, num_random=None):
    '''returns a dict with the UDIM number as key and a list of uv values as the value.
    Note that the uvs are in the form of a grid in that we can only pass in integers that 
    defines the number of items in each direction (u and v) and based on those numbers it
    creates a "grid" with the first value at uv (0,0).'''

    num_items_per_patch = num_items_u * num_items_v
    max_patches_u = 10

    udim_dict = {}
    for index in range(start_index, (num_items + start_index)):
        
        # if num_random is specified (int) set the index to be a random
        # number between start_index -> start_index + num_random
        if num_random is not None:
            index = start_index + random.randint(0, (num_random-1))
            
        # local uv (to each patch)
        local_u = (index % num_items_u) / float(num_items_u)
        local_v = ((index / num_items_u) % num_items_v) / float(num_items_v)
        
        #print(local_u, local_v)
        
        # patch index
        patch_index_u = (index / num_items_per_patch) % max_patches_u
        patch_index_v = index / (num_items_per_patch * max_patches_u)
        
        u = patch_index_u + local_u
        v = patch_index_v + local_v
                
        udim = 1000 + (patch_index_u + 1) + (max_patches_u * patch_index_v)

        # create a key in the dict using the udim
        if udim not in udim_dict:
            udim_dict[udim] = []

        udim_dict[udim].append((u,v))
                
    return udim_dict


def set_uvs(node_list):
    
    (u_min, u_max), (v_min, v_max) = pm.polyEvaluate(pm.polyListComponentConversion(node_list[0], tuv=True), boundingBox2d=True)
    uv_width = u_max - u_min
    uv_height = v_max - v_min
    
    max_num_items_u = int(math.floor(1.0 / uv_width))
    max_num_items_v = int(math.floor(1.0 / uv_height))
    #print(max_num_items_u, max_num_items_v)
    
    
    left_edge_offset = 0.015
    bottom_edge_offset = 0.015
    
    
    num_items = len(node_list)
    
    # hardcoded values, change later
    num_items_u = 5
    num_items_v = 5
    num_items_per_patch = num_items_u * num_items_v
    start_index = 0
    num_random = None
    
    #diff_u = (1.0 / num_items_u) -uv_width
    #diff_v = (1.0 / num_items_v) -uv_height
    
    
    udim_dict = udim_from_index(num_items_u=num_items_u, num_items_v=num_items_v, num_items=num_items, start_index=start_index, num_random=num_random)
    #pprint.pprint(uv_dict)
    
    # step through the udim dict. The dict has the udim as keys with a list of the uv coords as value
    # note that the uvs are returned in the uv list as a uniform grid. To offset the fom the grid lines,
    # i.e. to be able to set a zero spacing between or the be able to set an arbitrary spacing, we first
    # need to renome the default spacing we get from the udim_from_index method.
    #se what we could do is to calculate the differnence of the actual uv shell from the grid spacing we
    #get from the udim_from_index method, and then subtract that difference, and then add the margin of
    #our choice.
    index = 0
    for udim in sorted(udim_dict):
                
        for uv in udim_dict[udim]:
            
            node_uvs = pm.polyListComponentConversion(node_list[index], tuv=True)
            (u_min, u_max), (v_min, v_max) = pm.polyEvaluate(node_uvs, boundingBox2d=True)
            
            u = -u_min + uv[0] + left_edge_offset
            v = -v_min + uv[1] + bottom_edge_offset
            
            pm.polyEditUV(node_uvs, u=u, v=v)
                                   
            index += 1
        
    
    
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
    
    
'''
num_items_u = 2
num_items_v = 2
num_items = 40
start_index = 0
num_random = None

uv_dict = udim_from_index(num_items_u=num_items_u, num_items_v=num_items_v, num_items=num_items, start_index=start_index, num_random=num_random)
pprint.pprint(uv_dict)
'''

pm.openFile("/Users/johan/Documents/Projects/python_dev/scenes/plane_grid.mb", f=True)
node_list = [pm.PyNode('pPlane{0}'.format(n+1)) for n in range(50)]
pm.select(node_list)

set_uvs(node_list)

    
    
    