import pymel.core as pm
import maya.mel as mel
#import petfactory.util.dev as dev
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

def add_follicle_to_mesh(mesh_shape, u, v):

    if not isinstance(mesh_shape, pm.nodetypes.Mesh):
        pm.warning('Please select a mesh')
        return None

    follicle_shape = pm.createNode('follicle')
    follicle_transform = follicle_shape.getParent()
    
    mesh_shape.outMesh >> follicle_shape.inputMesh
    mesh_shape.worldMatrix[0] >> follicle_shape.inputWorldMatrix
    
    follicle_shape.outTranslate >> follicle_transform.translate
    follicle_shape.outRotate >> follicle_transform.rotate
    
    follicle_shape.parameterU.set(u)
    follicle_shape.parameterV.set(v)
    
    return follicle_transform
    

def face_uv_midpoint(face):
    
    if not isinstance(face, pm.nodetypes.general.MeshFace):
        pm.warning('Please select a mesh face')
        return None
    
    vert_list = face.getVertices()
    num_vert = len(vert_list)
    
    u = 0
    v = 0
    for vert in vert_list:
        uv = plane_shape.getUV(vert)
        u += uv[0]
        v += uv[1]
        
    u, v = u/num_vert, v/num_vert
        
    return(u,v)

''' 
dev.del_transform()
    
plane = pm.polyPlane(sw=5, sh=5)[0]
plane_shape = plane.getShape()

#mel.eval('ToggleVertIDs')
#mel.eval('ToggleFaceIDs')

face = pm.ls(sl=True)[0]

uv = face_uv_midpoint(face)

if uv:
    u, v = uv
    follicle_transform = add_follicle_to_mesh(plane_shape, u, v)
'''