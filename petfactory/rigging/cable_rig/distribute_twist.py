import pymel.core as pm

pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/empty_scene.mb', f=True)

num_joints = 10

start_ctrl = pm.circle(name='start', normal=(0,1,0))[0]
start_ctrl.translate.set(0,num_joints-1,0)
end_ctrl = pm.circle(name='start', normal=(0,1,0))[0]
pm.toggle([start_ctrl, end_ctrl], localAxis=True)


start_vec_prod = pm.createNode('vectorProduct', name='start_vector_prod')
start_vec_prod.operation.set(3)
start_vec_prod.input1.set(0,0,1)
start_vec_prod.normalizeOutput.set(True)
start_ctrl.worldMatrix[0] >> start_vec_prod.matrix


end_vec_prod = pm.createNode('vectorProduct', name='start_vector_prod')
end_vec_prod.operation.set(3)
end_vec_prod.input1.set(0,0,1)
end_vec_prod.normalizeOutput.set(True)
end_ctrl.worldMatrix[0] >> end_vec_prod.matrix


sp_start = pm.polySphere(r=.1)[0]
start_vec_prod.output >> sp_start.translate

sp_end = pm.polySphere(r=.1)[0]
end_vec_prod.output >> sp_end.translate

for index in range(num_joints):
    
    cube = pm.polyCube(h=.5, d=.5, w=.5)[0]
    cube.translate.set(0, index, 0)
    pm.toggle(cube, localAxis=True)