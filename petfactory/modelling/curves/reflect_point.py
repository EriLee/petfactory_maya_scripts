import pymel.core as pm
import math

# the hypoytenuse
crv = pm.PyNode('crv')
pos_list = crv.getCVs()

refl_vec = pos_list[1] - pos_list[0]

obj = pm.PyNode('dot_1')
obj_pos = obj.translate.get()

'''
reflection

V = vector beeing reflected
L = Any vector in the line beeing reflected in
ref_vec = 2 * V.dot(L) / V.dot(L) * L - V

'''

v_r = 2 * obj_pos.dot(refl_vec) / refl_vec.dot(refl_vec) * refl_vec - obj_pos


dup = pm.duplicate(obj)[0]
dup.translate.set(v_r)


