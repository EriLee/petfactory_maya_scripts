import maya.cmds as cmds
import maya.mel as mel


def make_crv_dynamic(crv):
    
    #crv_shape = cmds.listRelatives( crv, s=True, pa=True )[0]
    
    cmds.select(crv)
    mel.eval( 'makeCurvesDynamicHairs 1 0 1;' )
    
    
    follicle = cmds.listRelatives( crv, p=True, pa=True )[0]
    hairsystem = cmds.listConnections( '%s.outHair' % follicle)[0]
    outcurve = cmds.listConnections( '%s.outCurve' % follicle)
    nucleus = cmds.listConnections( '%s.currentState' % hairsystem)
    
    return (follicle, hairsystem, outcurve, nucleus)


a = make_crv_dynamic('curve1')
print(a)