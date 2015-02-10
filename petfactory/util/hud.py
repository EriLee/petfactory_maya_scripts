from functools import partial
import pymel.core as pm

def print_attr(node, attr):
	try:
	    return(pm.getAttr('{0}.{1}'.format(node, attr)))
	except:
		return 'no data'


def add_hud(node, attr, action):
    
    hud_name = 'hud_{0}'.format(attr)
    next_block = pm.headsUpDisplay(nextFreeBlock=1)
    pm.headsUpDisplay(hud_name, section=1, block=next_block, blockSize='medium', label=attr, labelFontSize='large', command=partial(print_attr, node, attr), attachToRefresh=True)
    
    return hud_name


node = pm.PyNode('hairSystemShape1')

hud_list = []
hud_list.append(add_hud(node, 'startCurveAttract', print_attr))
hud_list.append(add_hud(node, 'damp', print_attr))
hud_list.append(add_hud(node, 'stretchDamp', print_attr))


def remove_hud(hud_list):
    for hud in hud_list:
        pm.headsUpDisplay(hud, rem=True)
        
    

remove_hud(hud_list)