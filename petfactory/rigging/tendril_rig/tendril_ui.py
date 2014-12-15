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
        self.setWindowTitle("Tendril Setup")
        
        
        # layout
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        # tendril name
        self.name_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.name_horiz_layout)
        
        self.name_label = QtGui.QLabel('Tendril Name')
        self.name_horiz_layout.addWidget(self.name_label)
        
        self.name_line_edit = QtGui.QLineEdit()
        self.name_horiz_layout.addWidget(self.name_line_edit)
          
        # tree view
        self.model = QtGui.QStandardItemModel()
        self.tree_view = QtGui.QTreeView()
        self.tree_view.setModel(self.model)
        self.vertical_layout.addWidget(self.tree_view)
        self.tree_view.header().setVisible(False)
        
        # add joint ref
        self.joint_ref_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.joint_ref_horiz_layout)        
        
        self.add_joint_ref_button = QtGui.QPushButton('Add Joint ref group')
        self.add_joint_ref_button.setMinimumWidth(125)
        self.joint_ref_horiz_layout.addStretch()
        self.joint_ref_horiz_layout.addWidget(self.add_joint_ref_button)
        self.add_joint_ref_button.clicked.connect(self.add_joint_ref_click)
        

        # Setup
        self.setup_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.setup_horiz_layout)
        
        self.import_button = QtGui.QPushButton('Setup Tendrils')
        self.import_button.setMinimumWidth(125)
        self.setup_horiz_layout.addStretch()
        self.setup_horiz_layout.addWidget(self.import_button)
        self.import_button.clicked.connect(self.import_data)
        
        
        self.vertical_layout.addStretch()
        

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
            item.setCheckable(True)
            item.setCheckState(QtCore.Qt.Checked)
            self.model.appendRow(item) 
                
        
    def import_data(self):
        
        ref_grp_list = []
        
        root = self.model.invisibleRootItem()
        num_children = self.model.rowCount()
    
        for i in range(num_children):
            
            child = root.child(i)
            
            if child.checkState():
                
                ref_grp_list.append(child.text())
                

        name = self.name_line_edit.text()
        
        
        # try to convert to a pymel camera node
        '''
        try:
            ref = pm.PyNode(joint_ref_grp)
            
        except pm.general.MayaNodeError as e:
            pm.warning('Object specified is not a valid transform!')
            return
        '''
        
        print(ref_grp_list, name)
            

def show():      
    win = Import_nuke_2d_track_ui(parent=maya_main_window())
    win.show()
    
show()