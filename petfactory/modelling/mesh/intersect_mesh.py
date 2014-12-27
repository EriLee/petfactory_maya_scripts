import maya.api.OpenMaya as om
import pymel.core as pm


def intersect_mesh(pos, vec, mesh_name):
    
    selectionList = om.MSelectionList()
    selectionList.add(mesh_name)
    dagPath = selectionList.getDagPath(0)
    fnMesh = om.MFnMesh(dagPath)

    intersection = fnMesh.closestIntersection(  om.MFloatPoint(pos),
                                                om.MFloatVector(vec),
                                                om.MSpace.kWorld, 99999, False)
    if intersection:
    
        hitPoint, hitRayParam, hitFace, hitTriangle, hitBary1, hitBary2 = intersection
        
        if hitTriangle > -1:
            return hitPoint
            

mesh_name = 'pSphere1'

crv = pm.PyNode('curve1')
crv_shape = crv.getShape()
cv_list = crv_shape.getCVs(space='world')

cv_vec = (cv_list[1] - cv_list[0]).normal()
pos = om.MPoint(cv_list[1])
vec = om.MVector(cv_vec)


hit_point = intersect_mesh(pos, vec, mesh_name)
loc = pm.spaceLocator()
loc.translate.set(hit_point)