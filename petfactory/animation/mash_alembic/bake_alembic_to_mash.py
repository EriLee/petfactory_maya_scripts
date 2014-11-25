import pymel.core as pm


frame_start = 0
frame_end = 100

sel_list = pm.ls(sl=True)

source, target = sel_list[0], sel_list[1]

# start stepping through the timeline, gatering anim data
for frame in range(frame_start, frame_end+1):
    
    pm.currentTime(frame, update=True, edit=True)
    m = source.getMatrix()
    target.setMatrix(m)
    pm.setKeyframe(target, attribute=['translate', 'rotate'], t=frame)
        