import petfactory.util.vector as pet_vector
import petfactory.util.dev as pet_dev


pet_dev.del_transform()
#help(pet_vector.interpolate_positions)

#interpolate_positions(pos_list, num_divisions=1)
num_div = 2
jnt_pos_list = [(0,0,0), (5,5,0), (10,0,0), (15,5,0)]
num_joints = len(jnt_pos_list)
pos_list = pet_vector.interpolate_positions(pos_list=jnt_pos_list, num_divisions=num_div)

crv = pm.curve(d=1, p=pos_list)
crv_shape = crv.getShape()
num_cvs = crv_shape.numCVs()

pm.toggle(crv_shape, cv=True)

clust_handle_grp_list = []
for cv in range(0, num_cvs-1, num_div+1):
    
    if cv < num_cvs - num_div - 2:
        clust, clust_handle = pm.cluster('{0}.cv[{1}:{2}]'.format(crv, cv, cv+num_div))
  
    else:
        clust, clust_handle = pm.cluster('{0}.cv[{1}:{2}]'.format(crv, cv, cv+num_div+1))

    pos = crv_shape.getCV(cv)
    clust_handle.getShape().origin.set(pos)
    clust_handle.setPivots(pos)
    clust_handle_grp_list.append(pm.group(clust_handle))

pm.select(deselect=True)

jnt_list = []
for p in jnt_pos_list:
    jnt_list.append(pm.joint(p=p))

pm.toggle(jnt_list, la=True)
pm.joint(jnt_list, e=True, oj='xyz', secondaryAxisOrient='yup')

for index, clust_handle_grp in enumerate(clust_handle_grp_list):
    pm.parent(clust_handle_grp, jnt_list[index])
