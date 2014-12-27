import pymel.core as pm
import math

sel_list = [pm.PyNode('pPlane{0}'.format(x)) for x in range(2)]

def get_z_axis(obj, axis):
    tm = obj.getMatrix()
    return(pm.datatypes.Vector(tm[axis][0], tm[axis][1], tm[axis][2]))


dest_y_axis = get_z_axis(sel_list[1], 1)
dest_z_axis = get_z_axis(sel_list[1], 2)

child_z_axis = get_z_axis(sel_list[0], 2)


proj_u = child_z_axis.dot(dest_z_axis)
proj_v = child_z_axis.dot(dest_y_axis)




theta = math.atan2(proj_v, proj_u)
theta_deg = pm.util.degrees(theta)

# Just add 360° if the answer from atan2 is less than 0°.
if theta_deg < 0:
    theta_deg = theta_deg+360


rx = sel_list[0].rotate.get()
dest_rx = rx[0] + theta_deg
sel_list[0].rotate.set((dest_rx, rx[1], rx[2]))
