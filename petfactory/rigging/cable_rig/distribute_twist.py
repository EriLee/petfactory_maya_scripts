import pymel.core as pm

pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/empty_scene.mb', f=True)

num_joints = 5

start_ctrl = pm.circle(name='start', normal=(0,1,0))[0]
start_ctrl.translate.set(0,num_joints-1,0)
end_ctrl = pm.circle(name='start', normal=(0,1,0))[0]
pm.toggle([start_ctrl, end_ctrl], localAxis=True)


start_vec_prod = pm.createNode('vectorProduct', name='start_vector_prod')
start_vec_prod.operation.set(3)
start_vec_prod.input1.set(0,0,1)
start_vec_prod.normalizeOutput.set(True)
start_ctrl.worldMatrix[0] >> start_vec_prod.matrix


end_vec_prod = pm.createNode('vectorProduct', name='end_vector_prod')
end_vec_prod.operation.set(3)
end_vec_prod.input1.set(0,0,1)
end_vec_prod.normalizeOutput.set(True)
end_ctrl.worldMatrix[0] >> end_vec_prod.matrix


#sp_start = pm.polySphere(r=.1)[0]
#start_vec_prod.output >> sp_start.translate

#sp_end = pm.polySphere(r=.1)[0]
#end_vec_prod.output >> sp_end.translate

# create joints
joint_list = [ pm.createNode('joint', ss=True) for n in range(num_joints)]

blend_inc = 1.0/(num_joints-1)
for index, jnt in enumerate(joint_list):
    
    print()
    
    jnt.translate.set(0, index, 0)
    pm.toggle(jnt, localAxis=True)
    
    blend_colors = pm.createNode('blendColors', name='test')
    blend_colors.blender.set(blend_inc*index)
    start_vec_prod.output  >> blend_colors.color1
    end_vec_prod.output  >> blend_colors.color2
    
    if index < num_joints-1:
        aim_const = pm.aimConstraint(joint_list[index+1], joint_list[index], aimVector=(1,0,0), upVector=(0,0,1), worldUpType='vector', worldUpVector=(0,0,1))
        
    else:
        aim_const = pm.aimConstraint(joint_list[index-1], joint_list[index], aimVector=(-1,0,0), upVector=(0,0,1), worldUpType='vector', worldUpVector=(0,0,1))
        
        
    blend_colors.output >> aim_const.worldUpVector
        
