import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as om
import math
import os
import pprint
import json


############################################

# write Maya data

############################################

def create_maya_anim_curve(name, attr):
    
    # translate
    if attr in ('tx', 'ty','tz'):
        return 'createNode animCurveTL -n "{0}_{1}";\n'.format(name, attr)
    
    # rotate
    elif attr in ('rx', 'ry','rz'):
        return 'createNode animCurveTA -n "{0}_{1}";\n'.format(name, attr)
    
    # scale
    elif attr in ('sx', 'sy','sz'):
        return 'createNode animCurveTU -n "{0}_{1}";\n'.format(name, attr)
        
    # the focal length needs to be attatched to the shape
    elif attr in ('focalLength'):
        return 'createNode animCurveTU -n "{0}Shape_{1}";\n'.format(name, attr)
        
    else:
        print('{0}.{1} not a valid attr'.format(name, attr))
        return None
      
def build_maya_ascii(data_dict): 
      
    attr_to_animate_list = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'focalLength']

    info = data_dict.get('info')
    #fps = info['fps']
    time_unit = info['time_unit']
    linear_unit = info['linear_unit']
    angle_unit = info['angle_unit']
    frame_start = info['frame_start']
    frame_end = info['frame_end']
    w = info['width']
    h = info['height']
    dar = info['device_aspect_ratio']
    pa = info['pixel_aspect']
    num_frames = frame_end - frame_start
    maya_version = info.get('maya_version')

    # write tha Maya ascii scene data
    s = '//Maya ASCII {0} scene\n\n'.format(maya_version)
    #s += '//petfactory.se\n'
    s += 'requires maya "{0}";\n'.format(maya_version)
    s += 'currentUnit -l {0} -a {1} -t {2};\n\n'.format(linear_unit, angle_unit, time_unit)
    s += 'select -ne :defaultResolution;\n\tsetAttr ".w" {0};\n\tsetAttr ".h" {1};\n\tsetAttr ".pa" {2};\n\tsetAttr ".dar" {3};\n\n'.format(w, h, pa, dar)
    
    # the data_dict is a dict with "camera" and "null" as keys holding lists 
    # of dicts of the camera and null obj with their info and keyframedata.
    
    attr_con_list = []
    
    for obj_type, obj_list in data_dict.iteritems():
        
        # skip the info dict
        if obj_type is 'info':
            continue

        for obj_dict in obj_list:                 
             
            for name, attr_dict in obj_dict.iteritems():

                # convert maya hierarchy pipes to underscores
                # add null to null name so it can be used in AE
                if obj_type == 'camera':
                    name = name.replace('|', '_') 
                    h_aperture = attr_dict.get('h_aperture')[0]
                    v_aperture = attr_dict.get('v_aperture')[0]
                    
                elif obj_type == 'null':
                    name = 'null_{0}'.format(name.replace('|', '_'))
                
                                      
                anim_crv_str = ''
                static_attr_dict = {}
                static_t = False
                static_r = False
                static_s = False
                
                # iterate through the attr and value_lists
                for attr, value_list in attr_dict.iteritems():
                    
                    '''
                    # get the camera apperture skip these attrs
                    if attr is 'v_aperture':
                        v_aperture = value_list[0]
                        continue
                        
                    elif attr is 'h_aperture':
                        h_aperture = value_list[0]
                        continue
                    '''


                    # continue if the attr is not supposed to be animated  
                    if attr not in attr_to_animate_list:
                        continue

                    
                    # if length of value_list is less than 2 it is a static value
                    if len(value_list) < 2:
                        static_attr_dict[attr] = value_list[0]
                        
                    # the attr is animated.
                    else:
                        # create anim curve node
                        anim_crv_str += create_maya_anim_curve(name, attr)
                        
                        # set the keyframe data
                        kf_list_string = ''.join([ '{0} {1} '.format(v[0] + frame_start, v[1]) for v in enumerate(value_list)])
                        anim_crv_str += '\tsetAttr -s {0} ".ktv[0:{1}]"  {2};\n\n'.format(num_frames+1, num_frames, kf_list_string)
                        
                        # store the nodes, so we can connect them later in the script
                        attr_con_list.append((name, attr))
                        
                        
                             
                # create the transform and shape
                s += '//{0}\n\n'.format(name)
                s += 'createNode transform -n "{0}";\n'.format(name)
                
                if 'tx' in static_attr_dict or 'ty' in static_attr_dict or 'tz' in static_attr_dict:
                    static_t = True
                    tx = static_attr_dict.get('tx') or attr_dict.get('tx')[0]
                    ty = static_attr_dict.get('ty') or attr_dict.get('ty')[0]
                    tz = static_attr_dict.get('tz') or attr_dict.get('tz')[0]

                if 'rx' in static_attr_dict or 'ry' in static_attr_dict or 'rz' in static_attr_dict:
                    static_r = True
                    rx = static_attr_dict.get('rx') or attr_dict.get('rx')[0]
                    ry = static_attr_dict.get('ry') or attr_dict.get('ry')[0]
                    rz = static_attr_dict.get('rz') or attr_dict.get('rz')[0]
                        
                if 'sx' in static_attr_dict or 'sy' in static_attr_dict or 'sz' in static_attr_dict:
                    static_s = True
                    sx = static_attr_dict.get('sx') or attr_dict.get('sx')[0]
                    sy = static_attr_dict.get('sy') or attr_dict.get('sy')[0]
                    sz = static_attr_dict.get('sz') or attr_dict.get('sz')[0]
                    
            # if we have some static attr set them
            # translate
            if static_t:
                s += '\tsetAttr ".t" -type "double3" {0} {1} {2};\n'.format(tx, ty, tz)
                
            # rotate
            if static_r:
                s += '\tsetAttr ".r" -type "double3" {0} {1} {2};\n'.format(rx, ry, rz)
               
            # scale 
            if static_s:
                s += '\tsetAttr ".s" -type "double3" {0} {1} {2};\n'.format(sx, sy, sz)
                
                
            # create the shape nodes
            if obj_type == 'camera':
                s += '\ncreateNode camera -n "{0}Shape" -p "{0}";\n'.format(name)
                s += '\tsetAttr ".cap" -type "double2" {0} {1};\n\n'.format(h_aperture, v_aperture)
                    
            elif obj_type == 'null':
                s += '\ncreateNode locator -n "{0}Shape" -p "{0}";\n\n'.format(name)
                    
            
            # finally add the anim curve nodes
            s += anim_crv_str
            

    # connect the objects with the anim curve nodes
    s += '//connect the anim crvs\n\n'
    for name, attr in attr_con_list:
        
        if attr is 'focalLength':
            s += 'connectAttr "{0}Shape_{1}.o" "{0}Shape.{1}";\n'.format(name, attr)
        else:
            s += 'connectAttr "{0}_{1}.o" "{0}.{1}";\n'.format(name, attr)


    return s


############################################

# write Nuke data

############################################

def build_nuke_anim_curves(attr_dict, an_attr_keys_list, knob_name, frame_start):
    
    s = '{%s} { ' %(knob_name)
        
    for attr in an_attr_keys_list:
        
        value_list = attr_dict.get(attr)
        s += ' {curve %s}' %(' '.join([ 'x{0} {1}'.format(i + frame_start, v) for i,v in enumerate(value_list) ]))
    
    s += '}\n'
    return s
    
def null_dict_to_nuke_axis(a_dict, an_index, node_slot_width, frame_start):
    
    # get the name of the first key, this is the node name
    name = a_dict.keys()[0]
        
    # use the key to access the list of attr dicts
    attr_dict = a_dict.get(name)

    s = 'Axis {\n'
    s += 'inputs 0 \n'
    s += 'xpos {0} \n'.format(an_index * node_slot_width)
    s += 'name {0}\n'.format(name)
    s += 'rot_order {0} '.format(attr_dict['rotation_order'][0])
    s += build_nuke_anim_curves(attr_dict, ['tx', 'ty', 'tz'], 'translate', frame_start)
    s += build_nuke_anim_curves(attr_dict, ['rx', 'ry', 'rz'], 'rotate', frame_start)
    s += build_nuke_anim_curves(attr_dict, ['sx', 'sy', 'sz'], 'scaling', frame_start)
    s += '}\n'
  
    return s
      
def cam_dict_to_nuke_camera(a_dict, an_index, offset_x, node_slot_width, scene_y_offset, frame_start):
    
    name = a_dict.keys()[0]
    attr_dict = a_dict.get(name)
    
    s = 'Camera {'
    s += 'name {0} '.format(name)
    s += 'rot_order {0} '.format(attr_dict['rotation_order'][0])
    s += 'inputs 0 '
    s += 'xpos {0} '.format(offset_x + (an_index +2) * node_slot_width)
    s += 'ypos {0} '.format(scene_y_offset)
    s += build_nuke_anim_curves(attr_dict, ['tx', 'ty', 'tz'], 'translate', frame_start)
    s += build_nuke_anim_curves(attr_dict, ['rx', 'ry', 'rz'], 'rotate', frame_start)
    s += build_nuke_anim_curves(attr_dict, ['focal_length'], 'focal', frame_start)
    s += 'haperture {0} vaperture {1} '.format(round(attr_dict["h_aperture"][0] * 25.4), round(attr_dict["v_aperture"][0] * 25.4))
    s += 'far {0} near {1} '.format(attr_dict["far_clip"][0], attr_dict["near_clip"][0])
    s += ' }\n'
       
    return s;
    
def build_nuke_nodes(anim_dict):
    
    node_slot_width = 70
    scene_y_offset = 150

    # get info
    frame_start = anim_dict.get('info').get('frame_start')
    #frame_end = anim_dict.get('info').get('frame_end')
    
    # get the nulls and camera dicts
    null_list = anim_dict.get("null")
    cam_list = anim_dict.get("camera")
    
    # init the return string 
    str = ''
    
    for index, dict in enumerate(null_list):

        str += null_dict_to_nuke_axis(dict, index, node_slot_width, frame_start)
        
    # calculate where to paste tha camera in the node graph
    cam_pos_x = ((len(null_list)-1)*.5) * node_slot_width
    str += 'Scene { '
    str += 'inputs {0} '.format(len(null_list))
    str += 'xpos {0} '.format(cam_pos_x)
    str += 'ypos {0} '.format(scene_y_offset)
    str += '}\n'    
    
    
    for index, dict in enumerate(cam_list):

        str += cam_dict_to_nuke_camera(dict, index, cam_pos_x, node_slot_width, scene_y_offset, frame_start)

    return str
    

# get scene and keyframe data
def build_anim_dict(sel_list, frame_start, frame_end):
    
    obj_list = []
    null_attr = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    cam_attr = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'focal_length', 'h_aperture', 'v_aperture', 'far_clip', 'near_clip']
    
    # gather scene info
    info_dict = {}
    
    time_format_dict = {'game':15, 'film':24, 'pal':25, 'ntsc':30, 'show':48, 'palf':50, 'ntscf':60}
    time_unit = pm.currentUnit(q=True, time=True)
    linear_unit = pm.currentUnit(q=True, linear=True)
    angle_unit = pm.currentUnit(q=True, angle=True)
    info_dict['time_unit'] = time_unit
    info_dict['linear_unit'] = linear_unit
    info_dict['angle_unit'] = angle_unit
    info_dict['fps'] = time_format_dict.get(time_unit)
    info_dict['frame_start'] = frame_start
    info_dict['frame_end'] = frame_end
    info_dict['width'] = pm.getAttr('defaultResolution.width')
    info_dict['height'] = pm.getAttr('defaultResolution.height')
    info_dict['device_aspect_ratio'] = pm.getAttr('defaultResolution.deviceAspectRatio')
    info_dict['pixel_aspect'] = pm.getAttr('defaultResolution.pixelAspect')
    info_dict['maya_version'] = cmds.about(version=True)
    
    # the name to use as the key in the dict, shortest unique or just the node name
    cache_name = []
    null_list = []
    cam_list = []
    ret_dict = {"null":null_list, "camera":cam_list, 'info':info_dict}
    
    # loop through all the selected objects.
    # if it is a camera we will store it in the camera dict, and use the cam_attr
    for sel in sel_list:
        
        # make sure the obj is a transform
        if not isinstance(pm.PyNode(sel), pm.nodetypes.Transform):
            print('is a NOT {0}'.format(sel))
            continue
        else:
            print('is a {0}'.format(sel))
            obj_list.append(sel)

        shape_node = sel.getShape()
        
        # if we have a shape node check if it is a camera
        if shape_node:
            is_camera = isinstance(pm.PyNode(shape_node), pm.nodetypes.Camera)
         
        # if shape_node is None we have selected an empty transform    
        else:
            is_camera = False
        
        attr_dict = {} # this is the dict that stores the nodes attrs
        
        # static attributes (that does not change over time)
        attr_dict['rotation_order'] = [cmds.getAttr('{0}.rotateOrder'.format(sel))]
        
        #if use_shortest_unique_name: n = obj.shortName() # the shortest unique
        #else: n = obj.nodeName() # just the node name
        
        # get the shortest unique name and store in the cache name list.
        # is used as a key in the nu
        n = sel.shortName()
        cache_name.append(n) # store the node nall_list and cam_listsme in a list for later use

        # Populate the attr dicts with dicts for each attribute, append the attr dict to 
        # the cam_ or null_list depending of the type of node we are operating on
        if is_camera:
            cam_list.append({n:attr_dict})
            
            # create the keys for the dict
            for x in cam_attr:
                attr_dict[x] = []
             
            # static attributes are collection putside the frame range loop
            ca = (pm.getAttr('{0}.cameraAperture'.format(shape_node)))
            attr_dict["h_aperture"] = [ca[0]]
            attr_dict["v_aperture"] = [ca[1]]
            attr_dict["far_clip"] = [shape_node.getFarClipPlane()]
            attr_dict["near_clip"] = [shape_node.getNearClipPlane()]

            
        else:
            null_list.append({n:attr_dict})
            
            # create the keys for the dict
            for x in null_attr:
                attr_dict[x] = []


    if len(obj_list) < 1:
        pm.warning('No valid objects were selected!')
        return None


    # start stepping through the timeline, gatering anim data
    for frame in range(frame_start, frame_end+1):
        
        # Index to be used to acces the correct dict in the cam and null_lists
        null_index = 0
        cam_index = 0 
        
        pm.currentTime(frame, update=True, edit=True)
            
         # The index (from the enumerator) will be used to access the node names   
        for index, obj in enumerate(obj_list):

            matrix = om.MTransformationMatrix(om.MMatrix(pm.xform(obj, q=True, ws=True, matrix=True)))
            translate = matrix.translation(1)
            rotation = matrix.rotation()
            scale = matrix.scale(1)
            
            shape = obj.getShape()
            if shape:
                is_camera = isinstance(pm.PyNode(shape), pm.nodetypes.Camera)
            else:
                is_camera = False
            
            if is_camera:
                                
                for attr in cam_attr:

                    if attr is 'tx': cam_list[cam_index][cache_name[index]]['tx'].append(translate.x)
                    elif attr is 'ty': cam_list[cam_index][cache_name[index]]['ty'].append(translate.y)
                    elif attr is 'tz': cam_list[cam_index][cache_name[index]]['tz'].append(translate.z)
                    elif attr is 'rx': cam_list[cam_index][cache_name[index]]['rx'].append((180/math.pi)*rotation.x)
                    elif attr is 'ry': cam_list[cam_index][cache_name[index]]['ry'].append((180/math.pi)*rotation.y)
                    elif attr is 'rz': cam_list[cam_index][cache_name[index]]['rz'].append((180/math.pi)*rotation.z)
                    elif attr is 'focal_length': cam_list[cam_index][cache_name[index]]['focal_length'].append(pm.getAttr('{0}.focalLength'.format(shape)))
                
                cam_index += 1
                
            else:
                
                for attr in null_attr:

                    if attr is 'tx': null_list[null_index][cache_name[index]]['tx'].append(translate.x)
                    elif attr is 'ty': null_list[null_index][cache_name[index]]['ty'].append(translate.y)
                    elif attr is 'tz': null_list[null_index][cache_name[index]]['tz'].append(translate.z)
                    elif attr is 'rx': null_list[null_index][cache_name[index]]['rx'].append((180/math.pi)*rotation.x)
                    elif attr is 'ry': null_list[null_index][cache_name[index]]['ry'].append((180/math.pi)*rotation.y)
                    elif attr is 'rz': null_list[null_index][cache_name[index]]['rz'].append((180/math.pi)*rotation.z)
                    elif attr is 'sx': null_list[null_index][cache_name[index]]['sx'].append(scale[0])
                    elif attr is 'sy': null_list[null_index][cache_name[index]]['sy'].append(scale[1])
                    elif attr is 'sz': null_list[null_index][cache_name[index]]['sz'].append(scale[2])
                    
                null_index += 1                
                        
    return ret_dict


def remove_static_attr(data_dict):
    
    '''removes all static channels i.e attributes that does not change over time.
    The threshold of the change is controlled by the diff variable. If the absolute change
    between frames are less then the threshold the attr is considered static and the list
    is replaced by the first scalar in the list. 
    
    Note that no copy is made of the dict. It will change the dict in place.
    
    '''
    
    diff = 0.00001
        
    for obj_type, obj_dict_list in data_dict.iteritems():
        
        if obj_type is 'info': continue
                            
        for obj_dict in obj_dict_list:
            
            for name, attr_dict in obj_dict.iteritems():
                
                for attr, value_list in attr_dict.iteritems():
                                        
                    for index, v in enumerate(value_list):
                        
                        if index is 0:
                            
                            last_v = v
                            end_frame = len(value_list)-1
                            
                        elif index < end_frame:
                            # check if the difference is greater then the diff threshold
                            # if it is the attr is animated so break
                            if abs(v - last_v) > diff:
                                #print('-- {0} not a static channel, break').format(attr)
                                break
                                
                            else:
                                last_v = v
                                
                        else:

                            if abs(v - last_v) < diff:
                                #print('{0}  -  reached end msut be static').format(attr)
                                #attr_dict[attr] = [round(value_list[0])]
                                attr_dict[attr] = [value_list[0]]

def scale_translate(info_dict, scale):
    
    def do_scale(attr_list):
        '''loop through and scale up the attrs'''
        for i, val in enumerate(attr_list):
                attr_list[i] = val * scale
                    
    def get_attr_dicts(node_dict_list):
        '''get to the attr dicts'''
        for node_dict in node_dict_list:
            
            for node, attr_dict in node_dict.iteritems():
                
                do_scale(attr_dict.get('tx'))
                do_scale(attr_dict.get('ty'))
                do_scale(attr_dict.get('tz'))
                
    
    get_attr_dicts(info_dict.get('null'))
    get_attr_dicts(info_dict.get('camera'))

    
def write_data(sel_list, frame_start, frame_end, file_format='json'):
    
    #use_shortest_unique_name = True
    do_remove_static_attr = True
    write_to_file = True

    curr_time = pm.currentTime(query=True)
    
    if len(sel_list) < 1:
        pm.warning('Select transform(s) and camera(s)')
        return
        
    else:
        data_dict = build_anim_dict(sel_list, frame_start, frame_end)
    
    # reset the time slider
    pm.currentTime(curr_time)

    # no valid objects were selected and None was returned
    if data_dict is None:
        return

    if do_remove_static_attr:
        remove_static_attr(data_dict)

    # scale attrs
    if True:
        scale_translate(data_dict, 1)

    if file_format is 'ma':
        # uses the imported "maya_exporter" module to write a maya ascii scene
        anim_data = build_maya_ascii(data_dict)

    elif file_format is 'nk':
        anim_data = build_nuke_nodes(data_dict)

    elif file_format is 'nk_copy':
        # uses the imported "maya_exporter" module to write a maya ascii scene
        write_to_file = False
        anim_data = build_nuke_nodes(data_dict)
        os.system("echo {0} | pbcopy".format('\'' + anim_data + '\'')) 
        
    elif file_format is 'json':
        # flat string
        #anim_data = json.dumps(data_dict)
        # pretty print
        anim_data = json.dumps(data_dict, sort_keys=True,indent=4, separators=(',', ': '))
        # copy to clipboard
        #os.system("echo {0} | pbcopy".format('\'' + anim_data + '\'')) 

    if write_to_file:

        file_path = pm.fileDialog2(fileFilter='*.{0}'.format(file_format), dialogStyle=2, fileMode=0)
        
        # open a file and write to disc
        if file_path:
            if isinstance(file_path, list): file_path = file_path[0]
            f = open(file_path,'w')
            f.write(anim_data)
            f.close()
        