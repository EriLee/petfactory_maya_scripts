import pymel.core as pm
import json

# read the json
read_data = None
with open('/Users/johan/Desktop/null_data.json', 'r') as f:
    read_data = f.read()


data = json.loads(read_data)
all_m = data.get('matrix')


frame_start = 0
frame_end = 25

curr_time = pm.currentTime(query=True)

for i in range(frame_start, frame_end):
    
    print(i)
    pm.currentTime(i, update=True, edit=True)
    m = all_m[i]
    tm = pm.datatypes.TransformationMatrix([m[0], m[1], m[2], 0], [m[3], m[4], m[5], 0], [m[6], m[7], m[8], 0], [m[9], m[10], m[11], 1])
    c.setMatrix(tm)
    pm.setKeyframe(c, attribute=['translate', 'rotate', 'scale'], t=i)
    
# reset the time slider
pm.currentTime(curr_time)



c = pm.PyNode('pCube1')