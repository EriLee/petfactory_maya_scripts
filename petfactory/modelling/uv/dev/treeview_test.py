from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
import pprint

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
# custom data
class MyCustomType(object):
    
    def __init__(self, data):
        self.data = data
        
class TreeviewTest(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(TreeviewTest, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(200,250)
        self.setWindowTitle("Tile group UV")
        
        # main vertical layout
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        
        # tree view
        self.model = QtGui.QStandardItemModel()
        
        self.tree_view = QtGui.QTreeView()
        self.tree_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tree_view.setAlternatingRowColors(True)
 
        
        self.tree_view.setModel(self.model)
        self.vertical_layout.addWidget(self.tree_view)
        
        self.model.setHorizontalHeaderLabels(['UV Tiles'])
        
        self.list_button = QtGui.QPushButton('Press Me')
        self.vertical_layout.addWidget(self.list_button)
        self.list_button.clicked.connect(self.list_button_clicked)
        
    
    def list_button_clicked(self):
        
        root = self.model.invisibleRootItem()
        num_rows = self.model.rowCount()
        selection_model = self.tree_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()
                
        sel_list = []
        for row_index in range(num_rows):
            
            item = root.child(row_index)
            q_index = item.index()
            #has_children = item.hasChildren()
            num_children = item.rowCount()
            
            # the parent item is selected
            if q_index in selected_indexes:
                #print('add the parent, containing all sub items')
                sel_list.append('PARENT')
                continue
                
            # the parent item is not selected, check if the
            # child item is selected and if so add to sel_list
            else:
                for n in range(num_children):
                    child = item.child(n)
                    if child.index() in selected_indexes:
                        sel_list.append(child.text())
                
        print(sel_list)
        
                
    def populate_model(self, grp_list):

        for index, grp in enumerate(grp_list):
            
            grp = grp_list[index][0]
            child_list = grp_list[index][1]
            
            item = QtGui.QStandardItem(grp.name())
            
            custom_data = MyCustomType(grp)
            item.setData(custom_data, QtCore.Qt.UserRole + 1)
                
            
            # set flags
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            
            for row_index, child in enumerate(child_list):
                
                child_item = QtGui.QStandardItem(child.name())
                
                custom_data = MyCustomType(child)
                
                item.setData(custom_data, QtCore.Qt.UserRole + 1)
            
                #item.appendRow(child_item)
                #PySide.QtGui.QStandardItem.setChild(row, column, item)
                item.setChild(row_index, 0, child_item)
            

            self.model.appendRow(item)

       


pm.openFile('/Users/johan/Documents/Projects/python_dev/scenes/treeview.mb', f=True)


try:
    win.close()
    
except NameError:
    print('No win to close')

win = TreeviewTest(parent=maya_main_window())
win.move(150,250)
win.show()


grp_list = [ pm.PyNode('group{0}'.format(n)) for n in range(4) ]

ret_list = []
for grp in grp_list:
        
    child_items = grp.listRelatives(c=True)
    ret_list.append((grp, child_items))
    
#pprint.pprint(ret_list)

win.populate_model(ret_list)