import pymel.core as pm
import maya.cmds as cmds
import pprint


pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/butterfly_rig_setup_scene_v01.mb', force=True)

front_axis = 'x'
up_axis = 'y'
crv = pm.PyNode('path')
mesh = pm.PyNode('butterfly_mesh')


crv_shape = crv.getShape()
min_u, max_u = crv_shape.getKnotDomain()

# create the joints
jnt_list = [pm.joint(name='{0}_jnt'.format(j)) for j in ['root', 'x', 'y', 'z']]


# create the motion path node, if fractionMode is True it will use 0-1 u range
motion_path = pm.pathAnimation(jnt_list[0], curve=crv, follow=True, bank=True, fractionMode=False, followAxis=front_axis, upAxis=up_axis, c=crv)


# set some keyframes
pm.setKeyframe(motion_path, v=0, attribute='uValue', t=1)
pm.setKeyframe(motion_path, v=max_u, attribute='uValue', t=100)



# perent the mesh
pm.parentConstraint(jnt_list[-1], mesh)