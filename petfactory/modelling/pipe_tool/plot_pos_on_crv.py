import pymel.core as pm
import maya.cmds as cmds
import pprint

pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/empty_scene.mb', f=True)


crv_theta = pm.curve(d=1, p=[(0,0,0),(8,0,0)])
crv_ang_diff = pm.curve(d=1, p=[(0,0,0),(8,0,0)])


radius = 3
theta = math.pi/6

ang_start = (1.5 * math.pi) - theta
ang_rest = (math.pi/2) - theta

#ang_opp = (180 - 90) - theta 
#ang_opp = 90 - theta
#ang_opp = (math.pi/2) - theta


#math.tan(theta) = o/a
#a * math.tan(theta) = o
#a = a / math.tan(theta)

adjacent = radius / math.tan(theta)





# visualize

crv_theta.rotate.set((0, 0, pm.util.degrees(theta)))
#crv_ang_diff.rotate.set((0, 0, pm.util.degrees(ang_opp)))

circ = pm.circle(radius=radius)[0]
circ.translate.set(adjacent, radius, 0)

