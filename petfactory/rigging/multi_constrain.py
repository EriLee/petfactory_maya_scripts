from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm

import petfactory.rigging.cable_rig.cable_setup as cable_setup


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
class MultiConstrainWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(MultiConstrainWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300,100)
        self.setWindowTitle("Multi Constrain")
        
        # main vertical layout
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        # target
        target_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(target_horiz_layout)
        
        self.target_button = QtGui.QPushButton('Add Target  > ')
        target_horiz_layout.addWidget(self.target_button) 
        self.target_button.clicked.connect(self.target_clicked)  
        
        self.target_line_edit = QtGui.QLineEdit()
        target_horiz_layout.addWidget(self.target_line_edit)
             
        
        
        # model
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Objects to Constrain'])
        
        # tree view
        self.tree_view = QtGui.QTreeView()
        self.tree_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tree_view.setAlternatingRowColors(True)
        self.vertical_layout.addWidget(self.tree_view)
        self.tree_view.setModel(self.model)
        
        # add objects layout
        self.joint_ref_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.joint_ref_horiz_layout)        
        
        # add
        self.add_object_button = QtGui.QPushButton(' + ')
        self.add_object_button.setMinimumWidth(40)
        self.joint_ref_horiz_layout.addWidget(self.add_object_button)
        self.add_object_button.clicked.connect(self.add_object_click)
        
        # remove
        self.remove_object_button = QtGui.QPushButton(' - ')
        self.remove_object_button.setMinimumWidth(40)
        self.joint_ref_horiz_layout.addWidget(self.remove_object_button)
        self.remove_object_button.clicked.connect(self.remove_object_click)
        
        # add / remove label
        self.joint_ref_label = QtGui.QLabel('Add / Remove objects')
        self.joint_ref_horiz_layout.addWidget(self.joint_ref_label)
        self.joint_ref_horiz_layout.addStretch()
        
        
        # maintain_offet_checkbox
        maintain_offset_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(maintain_offset_horiz_layout)
        
        self.maintain_offet_checkbox = QtGui.QCheckBox()
        maintain_offset_horiz_layout.addWidget(self.maintain_offet_checkbox)   
        
        self.maintain_offet_label = QtGui.QLabel('Maintain Offset')
        maintain_offset_horiz_layout.addWidget(self.maintain_offet_label)
        maintain_offset_horiz_layout.addStretch()
        
        
        # Setup
        setup_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(setup_horiz_layout)
        
        self.setup_button = QtGui.QPushButton('Constrain')
        self.setup_button.setMinimumWidth(80)
        setup_horiz_layout.addStretch()
        setup_horiz_layout.addWidget(self.setup_button)
        self.setup_button.clicked.connect(self.setup_clicked)
         
    @staticmethod
    def validate_pynode_transform(node):
        
        try:
            pynode = pm.PyNode(node)
            
            if isinstance(pynode, pm.nodetypes.Transform):
                return pynode
            else:
                return None
            
        except pm.MayaNodeError as e:
            return None
                                
        
    
    def target_clicked(self):
        
        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a target!')
            return
            
        target = MultiConstrainWidget.validate_pynode_transform(sel_list[0].longName())
        if target:
            self.target_line_edit.setText(sel_list[0].longName())
            
   
        
    def add_object_click(self):
        

        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a curve!')
            return

        
        for sel in sel_list:
        
            if not isinstance(sel, pm.nodetypes.Transform):
                pm.warning('{0} is not a valid transform, skipped'.format(sel.longName()))
                continue
            
            item = QtGui.QStandardItem(sel.longName())
            
            # set flags
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            
            item.setCheckable(True)
            item.setCheckState(QtCore.Qt.Checked)
            self.model.appendRow(item) 
                
    
    def remove_object_click(self):
        
        selection_model = self.tree_view.selectionModel()
        
        # returns QModelIndex
        selected_rows = selection_model.selectedRows()
        
        row_list = [sel.row() for sel in selected_rows]
        row_list.sort(reverse=True)
        
        for row in row_list:
            self.model.removeRow(row)
    
       
    def setup_clicked(self):
            
        root = self.model.invisibleRootItem()
        num_children = self.model.rowCount()
        obj_list = []
        
        for i in range(num_children):
            
            child = root.child(i)
            
            if child.checkState():
                
                node = MultiConstrainWidget.validate_pynode_transform(child.text())
                if node:
                    obj_list.append(node)
                
                # if we cant create a pynode, uncheck the item  
                else:
                    child.setCheckState(QtCore.Qt.Unchecked)
                                    

        if len(obj_list) < 1:
            pm.warning('Please specify 1 or more objects to constrain')
            return
            
        
        target = MultiConstrainWidget.validate_pynode_transform(self.target_line_edit.text())
        if target is None:
            pm.warning('The target object is not a valid transform')
            return
            
        
        maintain_offset = self.maintain_offet_checkbox.isChecked()

        print(obj_list, target, maintain_offset)
        
        for obj in obj_list:
            
            pm.parentConstraint(pm.PyNode(target), pm.PyNode(obj), mo=maintain_offset)   

def show():      
    win = MultiConstrainWidget(parent=maya_main_window())
    win.show()
    

#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/3deg_5cvs.mb', f=True)
#pm.select('curve0')

'''
try:
    win.close()
    
except NameError:
    print('No win to close')

win = MultiConstrainWidget(parent=maya_main_window())
win.show()

#win.add_joint_ref_click()

win.move(100,250)
'''
