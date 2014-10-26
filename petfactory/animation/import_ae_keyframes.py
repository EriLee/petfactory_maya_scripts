import pymel.core as pm
import maya.api.OpenMaya as om
import json
import math


# read the json
data = None
with open('/Users/johan/Desktop/_data_v04.json', 'r') as f:
    data = f.read()

#print(data)

json_data = json.loads(data)
null_list = json_data.get('null')
cam_list = json_data.get('camera')

    
def set_keyframes_from_matrix_lists(node_list, node_type):
        
    for node_dict in node_list:
        
        for name, attr_dict in node_dict.iteritems():
    
            if node_type is 'null':
                node = pm.spaceLocator(n=name)
                
            elif node_type is 'camera':
                node = pm.camera()[0]
        
            matrix_list = attr_dict.get('matrix')
            
            for index, m in enumerate(matrix_list):
                
                # create a open maya transformation matrix                         
                matrix = om.MMatrix([m[0][0], m[0][1], m[0][2], 0, m[1][0], m[1][1], m[1][2], 0, m[2][0], m[2][1], m[2][2], 0, m[3][0], m[3][1], m[3][2], 1])
                t_matrix = om.MTransformationMatrix(matrix)
                
                # get the euler rotation from the matrix (default rotation order is XYZ)
                rot_xyz = t_matrix.rotation()
                
                # reorder the euler angles to ZYX
                rot_zyx = rot_xyz.reorder(5)
                
                # get the translation
                translation = t_matrix.translation(1)
                
                
                # convert radians to degrees
                rx = (180/math.pi)*rot_zyx[0]
                ry = (180/math.pi)*rot_zyx[1]
                rz = (180/math.pi)*rot_zyx[2]
                
                # set the rotation of the object
                # we negate the y and z rotation the match after effects
                node.rx.set(rx)
                node.ry.set(ry*-1)
                node.rz.set(rz*-1)
                
                # we negate the y and z translation the match after effects
                node.tx.set(translation.x)
                node.ty.set(translation.y*-1)
                node.tz.set(translation.z*-1)
                
                # set some keyframes
                pm.setKeyframe(node, attribute=['translate', 'rotate'], t=index)
            
            
set_keyframes_from_matrix_lists(null_list, 'null')
#set_keyframes_from_matrix_lists(cam_list, 'camera')

'''
m = null_list[0].get('Null 1').get('matrix')[24]
om_matrix = om.MMatrix([m[0][0], m[0][1], m[0][2], 0, m[1][0], m[1][1], m[1][2], 0, m[2][0], m[2][1], m[2][2], 0, m[3][0], m[3][1], m[3][2], 1])
t_matrix = om.MTransformationMatrix(om_matrix)
t_matrix.asMatrix()

eur = t_matrix.rotation()

euler_angles = eur.reorder(5)

print([ (180/math.pi)*a for a in [euler_angles[0], euler_angles[1], euler_angles[2]]])
'''

    

                 
        
