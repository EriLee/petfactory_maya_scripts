import pymel.core as pm
import maya.mel as mel
#import pprint


def make_curve_dynamic(crv):

    pm.select(deselect=True)
    print(crv)
    pm.select(crv)
    mel.eval('makeCurvesDynamicHairs 1 0 1;')
    
    ret_dict = {}

    follicle = pm.listRelatives(crv, p=True, pa=True)[0]
    hairsystem = pm.listConnections( '%s.outHair' % follicle)[0]
    ret_dict['output_curve'] = pm.listConnections( '%s.outCurve' % follicle)[0]
    ret_dict['nucleus'] = pm.listConnections( '%s.currentState' % hairsystem)[0]

    ret_dict['follicle'] = follicle
    ret_dict['hairsystem'] = hairsystem
    
    return ret_dict


#a = make_curve_dynamic('curve1')
#pprint.pprint(a)