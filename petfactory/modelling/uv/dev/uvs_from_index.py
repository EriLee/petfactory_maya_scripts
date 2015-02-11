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
    
    
    spacing = .03
    left_edge_offset = .02
    bottom_edge_offset = .02
    
    
    num_items = len(node_list)
    
    # hardcoded values, change later
    num_items_u = 4
    num_items_v = 4
    num_items_per_patch = num_items_u * num_items_v
    start_index = 0
    num_random = None
    
    udim_dict = udim_from_index(num_items_u=num_items_u, num_items_v=num_items_v, num_items=num_items, start_index=start_index, num_random=num_random)
    #pprint.pprint(uv_dict)
    
    # step through the udim dict. The dict has the udim as keys with a list of the uv coords as value
    # note that the uvs are returned in the uv list as a uniform grid.
    index = 0
    for udim in sorted(udim_dict):
        
        # iterate through the uv_list
        for uv in (udim_dict[udim]):
                                    
            node_uvs = pm.polyListComponentConversion(node_list[index], tuv=True)
            (u_min, u_max), (v_min, v_max) = pm.polyEvaluate(node_uvs, boundingBox2d=True)
            
            # the uv are stored in a uniform grid, i.e. if we have 4 shells on one u row
            # the uv stored in the uv list will be [0, 25, 5, 75] on patch u 0 v 0
            # on patch u1 v0 it will be [1.0, 1.25, 1.5, 1.75]
            # here get the remainder of the uv to get the "fraction part"
            # this will later be used to multiply with the combined width all the uv shells per row.
            percent_u = uv[0] % 1
            percent_v = uv[1] % 1
            
            # here we get the patch "index" i.e. which patch we are on. this will be used to offset the
            # local uv shell to the global "position"
            patch_u = math.floor(uv[0] / 1.0)
            patch_v = math.floor(uv[1] / 1.0)
            
            spacing_u = spacing * (percent_u * num_items_u)
            spacing_v = spacing * (percent_v * num_items_v)
            
            u = -u_min + percent_u * (uv_width * num_items_u) + patch_u + spacing_u + left_edge_offset
            v = -v_min + percent_v * (uv_height * num_items_v) + patch_v + spacing_v + bottom_edge_offset
            
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
node_list = [pm.PyNode('pPlane{0}'.format(n+1)) for n in range(128)]
pm.select(node_list)

set_uvs(node_list)

    
    
    