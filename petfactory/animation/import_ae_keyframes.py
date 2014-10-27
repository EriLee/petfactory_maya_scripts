import pymel.core as pm
import maya.api.OpenMaya as om
import json
import math


# read the json
data = None
with open('/Users/johan/Desktop/_data_v12.json', 'r') as f:
    data = f.read()

#print(data)

json_data = json.loads(data)
null_list = json_data.get('nulls')
cam_list = json_data.get('cameras')
info = json_data.get('info')
start_frame = info.get('start_frame')

rotate_orders = {'xyz':0, 'yzx':1, 'zxy':2, 'xzy':3, 'yxz':4, 'zyx':5}

scene_scale = .1

  
def set_keyframes_from_matrix_lists(node_list, node_type):
        
    for node_dict in node_list:
        
        for name, attr_dict in node_dict.iteritems():
    
            rot_order = attr_dict.get('rotate_order')
            
            if node_type is 'null':
                node = pm.spaceLocator(n=name)
                node.rotateOrder.set(rot_order)
                
            elif node_type is 'camera':
                node = pm.camera()[0]
                node.rotateOrder.set(rot_order)
                cam_shape = node.getShape()
                focal_length_list = attr_dict.get('focal_length')
                
        
            matrix_list = attr_dict.get('matrix')
            
            for index, m in enumerate(matrix_list):
                
                # create a open maya transformation matrix                         
                #matrix = om.MMatrix([m[0][0], m[0][1], m[0][2], 0, m[1][0], m[1][1], m[1][2], 0, m[2][0], m[2][1], m[2][2], 0, m[3][0], m[3][1], m[3][2], 1])
                matrix = om.MMatrix([m[0], m[1], m[2], 0, m[3], m[4], m[5], 0, m[6], m[7], m[8], 0, m[9], m[10], m[11], 1])
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
                node.tx.set(translation.x*scene_scale)
                node.ty.set(translation.y*-scene_scale)
                node.tz.set(translation.z*-scene_scale)
                
                # set some keyframes
                pm.setKeyframe(node, attribute=['translate', 'rotate'], t=start_frame+index)
                

                if node_type is 'camera':
                    
                    cam_shape.focalLength.set(focal_length_list[index])
                    pm.setKeyframe(cam_shape, attribute='focalLength', t=start_frame+index)

            
            
set_keyframes_from_matrix_lists(null_list, 'null')
set_keyframes_from_matrix_lists(cam_list, 'camera')

