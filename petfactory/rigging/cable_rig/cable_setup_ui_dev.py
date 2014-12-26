from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
class Import_nuke_2d_track_ui(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(Import_nuke_2d_track_ui, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300,100)
        self.setWindowTitle("Cable Setup")
        
        
        # layout
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        # tendril name
        self.name_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.name_horiz_layout)
        
        self.name_label = QtGui.QLabel('Rig Name')
        self.name_horiz_layout.addWidget(self.name_label)
        
        self.name_line_edit = QtGui.QLineEdit()
        self.name_horiz_layout.addWidget(self.name_line_edit)
          
        # tree view
        self.model = QtGui.QStandardItemModel()
        
        self.tree_view = QtGui.QTreeView()
        self.tree_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        #self.tree_view.setSelectionMode(QtGui.QAbstractItemView.ContiguousSelection)
        
        #self.tree_view.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.tree_view.setAlternatingRowColors(True)
 
        
        self.tree_view.setModel(self.model)
        self.vertical_layout.addWidget(self.tree_view)
        
        self.model.setHorizontalHeaderLabels(['Ref curve', 'Name'])
        
        #header = self.tree_view.header()
        #header.setResizeMode(QtGui.QHeaderView.Stretch)
        #header.setVisible(False)
        
        # add joint ref
        self.joint_ref_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.joint_ref_horiz_layout)        
        
        # add
        self.add_joint_ref_button = QtGui.QPushButton(' + ')
        self.add_joint_ref_button.setMinimumWidth(40)
        
        self.joint_ref_horiz_layout.addWidget(self.add_joint_ref_button)
        self.add_joint_ref_button.clicked.connect(self.add_joint_ref_click)
        
        # remove
        self.remove_joint_ref_button = QtGui.QPushButton(' - ')
        self.remove_joint_ref_button.setMinimumWidth(40)
        
        self.joint_ref_horiz_layout.addWidget(self.remove_joint_ref_button)
        self.remove_joint_ref_button.clicked.connect(self.remove_joint_ref_click)
        
        self.joint_ref_label = QtGui.QLabel('Add / Remove ref curve')
        self.joint_ref_horiz_layout.addWidget(self.joint_ref_label)
        self.joint_ref_horiz_layout.addStretch()

        
        # share hairsystem
        self.share_hairsystem_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.share_hairsystem_horiz_layout)
        
        self.share_hairsystem_checkbox = QtGui.QCheckBox()
        self.share_hairsystem_horiz_layout.addWidget(self.share_hairsystem_checkbox)
        
        self.share_hairsystem_label = QtGui.QLabel('Share Hairsystem')
        self.share_hairsystem_horiz_layout.addWidget(self.share_hairsystem_label)
        self.share_hairsystem_horiz_layout.addStretch()
          
        #self.vertical_layout.addStretch()

        # Setup
        self.setup_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.setup_horiz_layout)
        
        self.import_button = QtGui.QPushButton('Setup Tendrils')
        self.import_button.setMinimumWidth(125)
        self.setup_horiz_layout.addStretch()
        self.setup_horiz_layout.addWidget(self.import_button)
        self.import_button.clicked.connect(self.import_data)
        
        
        
        

    def add_joint_ref_click(self):
        

        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a camera!')
            return

        
        for sel in sel_list:
        
            if not isinstance(sel, pm.nodetypes.Transform):
                pm.warning('{0} is not a valid transform, skipped'.format(sel.name()))
                continue
            
            item = QtGui.QStandardItem(sel.name())
            
            # set flags
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            
            item.setCheckable(True)
            item.setCheckState(QtCore.Qt.Checked)
            self.model.appendRow(item) 
                
    
    def remove_joint_ref_click(self):
        
        selection_model = self.tree_view.selectionModel()
        
        # returns QModelIndex
        selected_rows = selection_model.selectedRows()
        
        row_list = [sel.row() for sel in selected_rows]
        row_list.sort(reverse=True)
        
        for row in row_list:
            self.model.removeRow(row)
    
       
    def import_data(self):
        
        ref_grp_list = []
        
        root = self.model.invisibleRootItem()
        num_children = self.model.rowCount()
        share_hairsystem = self.share_hairsystem_checkbox.isChecked()
    
        for i in range(num_children):
            
            child = root.child(i)
            
            if child.checkState():
                
                ref_grp_list.append(child.text())
                

        name = self.name_line_edit.text()
        
        
        print(ref_grp_list, name, share_hairsystem)
            

def show():      
    win = Import_nuke_2d_track_ui(parent=maya_main_window())
    win.show()
    

pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/3deg_5cvs.mb', f=True)

pm.select('curve0')
try:
    win.close()
    
except NameError:
    print('No win to close')

win = Import_nuke_2d_track_ui(parent=maya_main_window())
win.show()

win.add_joint_ref_click()

win.move(100,250)


