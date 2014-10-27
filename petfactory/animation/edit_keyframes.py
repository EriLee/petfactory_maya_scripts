import pymel.core as pm


#num_keys = pm.keyframe(cube, attribute='ty', query=True, keyframeCount=True)

def shift_keyframes(obj_list, move_inc):

    for index, sel in enumerate(sel_list):
    
        print(sel)
        pm.keyframe(sel, edit=True,relative=True,timeChange=move_inc*index)


'''
sel_list = pm.ls(sl=True)
shift_keyframes(sel_list, 1)
'''