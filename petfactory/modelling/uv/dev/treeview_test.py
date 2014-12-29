import pymel.core as pm 


class TreeviewTest(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(TreeviewTest, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(200,250)
        self.setWindowTitle("Tile group UV")



pm.openFile('/Users/johan/Documents/Projects/python_dev/scenes/treeview.mb', f=True)


try:
    win.close()
    
except NameError:
    print('No win to close')

win = TreeviewTest(parent=maya_main_window())
win.move(150,250)
win.show()


grp_list = [ pm.PyNode('group{0}'.format(n)) for n in range(4) ]

for grp in grp_list:
    
    item = grp
    
    child_items = grp.listRelatives(c=True)
    
    print(item, child_items)
    


