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
        
          
        # tree view
        self.model = QtGui.QStandardItemModel()
        
        self.tree_view = QtGui.QTreeView()
        self.tree_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tree_view.setAlternatingRowColors(True)
 
        
        self.tree_view.setModel(self.model)
        self.vertical_layout.addWidget(self.tree_view)
        
        self.model.setHorizontalHeaderLabels(['Objects to Constrain'])
        
        
        
        # add ref curve
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
        
        self.joint_ref_label = QtGui.QLabel('Add / Remove objects')
        self.joint_ref_horiz_layout.addWidget(self.joint_ref_label)
        self.joint_ref_horiz_layout.addStretch()
                
        # Setup
        setup_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(setup_horiz_layout)
        
        self.setup_button = QtGui.QPushButton('Constrain')
        self.setup_button.setMinimumWidth(80)
        setup_horiz_layout.addStretch()
        setup_horiz_layout.addWidget(self.setup_button)
        self.setup_button.clicked.connect(self.setup_clicked)
         

    def add_object_click(self):
        

        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a curve!')
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
                
    
    def remove_object_click(self):
        
        selection_model = self.tree_view.selectionModel()
        
        # returns QModelIndex
        selected_rows = selection_model.selectedRows()
        
        row_list = [sel.row() for sel in selected_rows]
        row_list.sort(reverse=True)
        
        for row in row_list:
            self.model.removeRow(row)
    
       
    def setup_clicked(self):
        
        use_existing = self.use_existing_group_box.isChecked()
        existing_hairsystem = None
        
        # if we are to use an existing hairsystem, make sure that is is valid, if so get a ref to it
        if use_existing:
            existing_hairsystem_name = self.existing_hairsystem_line_edit.text()
            
            try:
                existing_hairsystem = pm.PyNode(existing_hairsystem_name)
                
            except pm.general.MayaNodeError as e:
                pm.warning('The hairsystem specified is not valid')
                return
                
            try:
                
                shape = existing_hairsystem.getShape()
                
                if not isinstance(shape, pm.nodetypes.HairSystem):
                    pm.warning('Please select a Hairsystem')
                    return
                
            except AttributeError as e:
                pm.warning('Please select a Hairsystem ', e)
                return
                
    
    
        root = self.model.invisibleRootItem()
        num_children = self.model.rowCount()
        ref_crv_list = []
        for i in range(num_children):
            
            child = root.child(i)
            
            if child.checkState():
                
                ref_crv_list.append(child.text())
                

        if len(ref_crv_list) < 1:
            pm.warning('Please specify 1 or more ref curves!')
            return
            



        name = self.name_line_edit.text()
        share_hairsystem = self.share_hairsystem_checkbox.isChecked()
        num_joints = self.num_joints_spinbox.value()
        cable_radius = self.cable_radius_spinbox.value()
        
        
        print(ref_crv_list, name, share_hairsystem, use_existing, existing_hairsystem, num_joints, cable_radius)
            

def show():      
    win = MultiConstrainWidget(parent=maya_main_window())
    win.show()
    

#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/3deg_5cvs.mb', f=True)
#pm.select('curve0')

try:
    win.close()
    
except NameError:
    print('No win to close')

win = MultiConstrainWidget(parent=maya_main_window())
win.show()

#win.add_joint_ref_click()

win.move(100,250)


