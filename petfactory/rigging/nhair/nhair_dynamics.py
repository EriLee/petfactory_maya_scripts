import pymel.core as pm
import maya.mel as mel
#import pprint


def make_curve_dynamic(crv, delete_out_curve_parent=False):

    #pm.select(deselect=True)
    #print(crv)
    pm.select(crv)
    mel.eval('makeCurvesDynamicHairs 0 0 1;')
    
    ret_dict = {}

    follicle = pm.listRelatives(crv, p=True, pa=True)[0]
    out_curve = pm.listConnections( '%s.outCurve' % follicle)[0]
    hairsystem = pm.listConnections( '%s.outHair' % follicle)[0]
    ret_dict['output_curve'] = out_curve
    ret_dict['nucleus'] = pm.listConnections( '%s.currentState' % hairsystem)[0]

    ret_dict['follicle'] = follicle
    ret_dict['hairsystem'] = hairsystem

    if delete_out_curve_parent:
        crv_parent = out_curve.getParent()
        pm.parent(out_curve, world=True)
        pm.delete(crv_parent)

    return ret_dict


#a = make_curve_dynamic('curve1')
#pprint.pprint(a)