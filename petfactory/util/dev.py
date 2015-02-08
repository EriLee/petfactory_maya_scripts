import pymel.core as pm

def del_transform:
	t_list = pm.ls(type='transform')
	del_list = [ x for x in t_list if not isinstance(x.getShape(), pm.nodetypes.Camera)]
	pm.delete(del_list)
