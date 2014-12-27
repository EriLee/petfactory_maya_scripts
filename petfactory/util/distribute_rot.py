import pymel.core as pm
#import math


def get_rot(obj, axis):
    start_m = pm.datatypes.TransformationMatrix(obj.getMatrix())
    rot = pm.util.degrees(start_m.getRotation())
    return rot[axis]


def interpolate_rotation(sel_list):

    start_obj = sel_list[0]
    end_obj = sel_list[-1]
       
    start_rot = get_rot(start_obj, 0)
    end_rot = get_rot(end_obj, 0)


    rot_range = end_rot - start_rot

    num = len(sel_list)-2
    rot_inc = float(rot_range) / (num+1)
    print(rot_inc)  

    for n in range(num):

        orig_rot = sel_list[n+1].rotate.get()
        rot_x = start_rot + (n+1)*rot_inc
        sel_list[n+1].rotate.set((rot_x, orig_rot[1], orig_rot[2]))



sel_list = pm.ls(sl=True)

interpolate_rotation(sel_list)