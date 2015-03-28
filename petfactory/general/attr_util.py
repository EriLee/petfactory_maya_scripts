import pymel.core as pm


def show_unlock_v():
    
    sel_list = pm.ls(sl=True)
    
    if not sel_list:
        pm.warning('Nothing is selected!')
    
    try:
        for sel in sel_list:
            sel.v.unlock()
            sel.v.set(True)
            
    except AttributeError as e:
        print(e)


def hide_lock_v():
    
    sel_list = pm.ls(sl=True)
    
    if not sel_list:
        pm.warning('Nothing is selected!')
       
    try: 
        for sel in sel_list:
            sel.v.set(False)
            sel.v.lock()
            
    except AttributeError as e:
        print(e)

