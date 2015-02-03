import pymel.core as pm

def make_dynamic(crv_transform, hairsystem=None, nucleus=None):
    
    # check that the hairs sytem is valid
    
    
    time = pm.PyNode('time1')   
     
     
    if hairsystem is None:
        hairsystem = pm.createNode('hairSystem',ss=True)

    
    if nucleus is None:
        nucleus = pm.createNode('nucleus',ss=True)
    
    
    # Warning: 'hairSystemShape1.currentState' is already connected to 'nucleus1.inputActive[0]'. # 
    # Warning: 'hairSystemShape1.startState' is already connected to 'nucleus1.inputActiveStart[0]'. # 
    # Warning: 'nucleus1.outputObjects[0]' is already connected to 'hairSystemShape1.nextState'. # 
    # Warning: 'nucleus1.startFrame' is already connected to 'hairSystemShape1.startFrame'. #   
    
    
    follicle = pm.createNode('follicle',ss=True)
    crv_shape = crv_transform.getShape()
    
    # set follicle attr
    follicle.restPose.set(1)
    follicle.degree.set(3)
    
    # rebuild crv
    rebuild_crv_node = pm.createNode('rebuildCurve')
    rebuild_crv_node.keepControlPoints.set(1)
    rebuild_crv_node.degree.set(1)
    
    rebuild_crv_shape = pm.createNode('nurbsCurve', parent=crv_transform)
    # this gives a warning, (but seesm fine?):
    # Warning: pymel.core.general : Could not create desired MFn. Defaulting to MFnDagNode.
    rebuild_crv_shape.visibility.set(0)
    crv_shape.worldSpace[0] >> rebuild_crv_node.inputCurve
    rebuild_crv_node.outputCurve >> rebuild_crv_shape.create
     
    out_crv_transform = pm.duplicate(crv_transform, n='out_crv')[0]
    out_crv_shape = out_crv_transform.getShape()
    
    # nucleus 3 inputs
    time.outTime >> nucleus.currentTime
    hairsystem.currentState >> nucleus.inputActive[0]
    hairsystem.startState >> nucleus.inputActiveStart[0]
    
    # hairsystem 4 inputs
    time.outTime >> hairsystem.currentTime
    follicle.outHair >> hairsystem.inputHair[0]
    nucleus.outputObjects[0] >> hairsystem.nextState
    nucleus.startFrame >> hairsystem.startFrame
    
    # follicle 3 inputs
    hairsystem.outputHair[0] >> follicle.currentPosition
    rebuild_crv_shape.local >> follicle.startPosition
    crv_transform.worldMatrix[0] >> follicle.startPositionMatrix    
    
    # out curve
    follicle.outCurve >> out_crv_shape.create
    
    pm.select(rebuild_crv_node)
    return {'hairsystem':hairsystem, 'nucleus':nucleus, 'outcurve':out_crv_transform, 'follicle':follicle}
    

pm.newFile(f=True)
# create the original curve
crv_transform = pm.curve(d=3, ep=[(0,0,0), (6,0,0)], n='orig_crv')

# make the curve dynamic
dynamic_dict = make_dynamic(crv_transform)

# move the cvs of the orig crv
crv_transform.getShape().setCVs([(0,0,0), (2,2,0), (4,-2,0), (6,0,0)])
crv_transform.getShape().updateCurve()

'''
hairsystem = dynamic_dict.get('hairsystem')
nucleus = dynamic_dict.get('nucleus')

crv = pm.PyNode('curve1')
dynamic_dict = make_dynamic(crv, hairsystem=hairsystem, nucleus=nucleus)
'''