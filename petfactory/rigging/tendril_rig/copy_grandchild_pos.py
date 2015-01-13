import pymel.core as pm


sel_list = pm.ls(sl=True)


def get_cluster_handles(grp):
    
    clust_handle_list = []
    
    grp_child = grp.listRelatives(children=True)
    
    for child in grp_child:
        clust_handle_list.append(child.listRelatives(children=True)[0])
        
    return clust_handle_list
    
    
source_list = get_cluster_handles(sel_list[0])
dest_list = get_cluster_handles(sel_list[1])


def copy_local_pos(source_list, dest_list):

    for index, source in enumerate(source_list):
        pos = source.translate.get()
        dest_list[index].translate.set(pos)
        print(pos, index)
 
        
copy_local_pos(source_list, dest_list)