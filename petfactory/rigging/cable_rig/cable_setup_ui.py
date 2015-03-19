from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
from functools import partial

import petfactory.gui.simple_widget as simple_widget
reload(simple_widget)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
class CableSetupWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(CableSetupWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300,100)
        self.setWindowTitle("Cable Setup")

 
        # layout
        vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(vertical_layout)
        vertical_layout.setContentsMargins(0,0,0,0)

        
        tab_widget = QtGui.QTabWidget()
        vertical_layout.addWidget(tab_widget)
        

        
        # tab widgts and layout
        # tab 1        
        tab_1 = QtGui.QWidget()
        tab_widget.addTab(tab_1, "Setup")  
        tab_1_vertical_layout = QtGui.QVBoxLayout(tab_1)
        
        # tab 2 
        tab_2 = QtGui.QWidget()
        tab_widget.addTab(tab_2, "Extra")  
        tab_2_vertical_layout = QtGui.QVBoxLayout(tab_2)

          
        # tree view
        self.model = QtGui.QStandardItemModel()
        
        self.tree_view = QtGui.QTreeView()
        self.tree_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tree_view.setAlternatingRowColors(True)
 

        self.tree_view.setModel(self.model)
        tab_1_vertical_layout.addWidget(self.tree_view)
        
        self.model.setHorizontalHeaderLabels(['Cable curves', 'Name'])
                
        # add joint ref
        self.joint_ref_horiz_layout = QtGui.QHBoxLayout()
        tab_1_vertical_layout.addLayout(self.joint_ref_horiz_layout)        
        
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
        
        self.joint_ref_label = QtGui.QLabel('Add / Remove curves')
        self.joint_ref_horiz_layout.addWidget(self.joint_ref_label)
        self.joint_ref_horiz_layout.addStretch()
        
        
        # rig group box
        rig_group_box = QtGui.QGroupBox("Rig Properties")
        tab_1_vertical_layout.addWidget(rig_group_box)
        rig_group_vert_layout = QtGui.QVBoxLayout()
        rig_group_box.setLayout(rig_group_vert_layout)
        
        
        
        # rig name
        self.name_horiz_layout = QtGui.QHBoxLayout()
        rig_group_vert_layout.addLayout(self.name_horiz_layout)
        
        self.name_label = QtGui.QLabel('Rig name')
        self.name_horiz_layout.addWidget(self.name_label)
        
        self.name_line_edit = QtGui.QLineEdit()
        self.name_horiz_layout.addWidget(self.name_line_edit)
        
        
        # add_spinbox(label, parent_layout, min=None, max=None, default=None, double_spinbox=False):
        self.name_start_index_spinbox = simple_widget.add_spinbox(label='Name start index', parent_layout=rig_group_vert_layout, min=0, max=999)
        self.cable_radius_spinbox = simple_widget.add_spinbox(label='Cable radius', parent_layout=rig_group_vert_layout, min=.1, max=999, default=1, double_spinbox=True)
        self.cable_ik_joints_spinbox = simple_widget.add_spinbox(label='Cable IK joints', parent_layout=rig_group_vert_layout, min=3, max=10, default=4)
        self.cable_bind_joints_spinbox = simple_widget.add_spinbox(label='Cable bind joints', parent_layout=rig_group_vert_layout, min=3, max=99, default=10)

        
        # hairsystem group box
        hairsystem_group_box = QtGui.QGroupBox("Hairsystem")
        tab_1_vertical_layout.addWidget(hairsystem_group_box)
        hairsystem_group_vert_layout = QtGui.QVBoxLayout()
        hairsystem_group_box.setLayout(hairsystem_group_vert_layout)
        
        # use existing hairsystem group box
        self.use_existing_group_box = QtGui.QGroupBox("Use existing")
        
        hairsystem_group_vert_layout.addWidget(self.use_existing_group_box)
        self.use_existing_group_box.setCheckable(True)
        self.use_existing_group_box.setChecked(False)
        use_existing_group_box_vert_layout = QtGui.QVBoxLayout()
        self.use_existing_group_box.setLayout(use_existing_group_box_vert_layout)
        self.use_existing_group_box.clicked.connect(self.hairsystem_groupbox_clicked)

        # use existing hairsystem widget
        self.use_existing_hairsystem_widget = QtGui.QWidget()
        
        # use existing hairsystem
        use_existing_group_box_vert_layout.addWidget(self.use_existing_hairsystem_widget)

        use_existing_hairsystem_horiz_layout = QtGui.QHBoxLayout()
        
        self.use_existing_hairsystem_widget.setLayout(use_existing_hairsystem_horiz_layout)
        
        add_existing_hairsystem_button = QtGui.QPushButton('Hairsystem >')
        use_existing_hairsystem_horiz_layout.addWidget(add_existing_hairsystem_button)
        add_existing_hairsystem_button.clicked.connect(self.add_hairsystem_clicked)
                
        self.existing_hairsystem_line_edit = QtGui.QLineEdit()
        use_existing_hairsystem_horiz_layout.addWidget(self.existing_hairsystem_line_edit)


        
        # share hairsystem
        # create new hairsystem group box
        self.create_new_group_box = QtGui.QGroupBox("Create new")
        self.create_new_group_box.clicked.connect(self.hairsystem_groupbox_clicked)
        hairsystem_group_vert_layout.addWidget(self.create_new_group_box)
        self.create_new_group_box.setCheckable(True)
        create_new_group_box_vert_layout = QtGui.QVBoxLayout()
        self.create_new_group_box.setLayout(create_new_group_box_vert_layout)
        
        
        
        
        self.share_hairsystem_widget = QtGui.QWidget()

        create_new_group_box_vert_layout.addWidget(self.share_hairsystem_widget)

        
        share_hairsystem_horiz_layout = QtGui.QHBoxLayout()
        self.share_hairsystem_widget.setLayout(share_hairsystem_horiz_layout)

        self.share_hairsystem_checkbox = QtGui.QCheckBox()
        share_hairsystem_horiz_layout.addWidget(self.share_hairsystem_checkbox)
        
        self.share_hairsystem_label = QtGui.QLabel('Share Hairsystem')
        share_hairsystem_horiz_layout.addWidget(self.share_hairsystem_label)
        share_hairsystem_horiz_layout.addStretch()
        
 

        # Setup
        self.setup_horiz_layout = QtGui.QHBoxLayout()
        tab_1_vertical_layout.addLayout(self.setup_horiz_layout)
        
        self.setup_button = QtGui.QPushButton('Setup Cables')
        self.setup_button.setMinimumWidth(125)
        self.setup_horiz_layout.addStretch()
        self.setup_horiz_layout.addWidget(self.setup_button)
        self.setup_button.clicked.connect(self.setup_cable)
        
        
        
        
        # extra (tab 2)
        # rig group box
        sets_group_box = QtGui.QGroupBox("Sets")
        tab_2_vertical_layout.addWidget(sets_group_box)
        sets_group_vert_layout = QtGui.QVBoxLayout()
        sets_group_box.setLayout(sets_group_vert_layout)
        
        
        self.mesh_set_lineedit = simple_widget.add_populate_lineedit(label='<  Mesh      ', parent_layout=sets_group_vert_layout, callback=self.populate_lineedit, kwargs={'type':'follicle'})
        self.start_ctrl_set_lineedit = simple_widget.add_populate_lineedit(label='<  Start ctrl', parent_layout=sets_group_vert_layout, callback=self.populate_lineedit, kwargs={'type':'mesh'})
        self.end_ctrl_set_lineedit = simple_widget.add_populate_lineedit(label='<  End ctrl  ', parent_layout=sets_group_vert_layout, callback=self.populate_lineedit)
        self.follicle_set_lineedit = simple_widget.add_populate_lineedit(label='<  Follicle  ', parent_layout=sets_group_vert_layout, callback=self.populate_lineedit)
        
        
        
        tab_2_vertical_layout.addStretch()
                
        
    def populate_lineedit(self, **kwargs):
        
        lineedit = kwargs.get('lineedit')
        #type = kwargs.get('type')
        
        sel = pm.ls(sl=True)
        if sel:
            lineedit.setText(sel[0].longName())
            #print(type)
        

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
            
            
    def hairsystem_groupbox_clicked(self):

        is_checked = self.sender().isChecked()
        
        if self.sender() is self.use_existing_group_box:
            self.create_new_group_box.setChecked(not is_checked)
        
        else:
            self.use_existing_group_box.setChecked(not is_checked)


    def add_hairsystem_clicked(self):
        
        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Select a hairsystem!')
            return
        
        try:

            shape = sel_list[0].getShape()
            
            if isinstance(shape, pm.nodetypes.HairSystem):
                self.existing_hairsystem_line_edit.setText(sel_list[0].longName())
                
            else:
                pm.warning('Select a hairsystem!')
            
        except AttributeError as e:
            pm.warning('Please select a Hairsystem ', e)
            return
            
            
    
    
    
       
    def setup_cable(self):
        

        root = self.model.invisibleRootItem()
        num_children = self.model.rowCount()
                
        # the ref grp
        if num_children < 1:
            pm.warning('No joint ref are available in the treeview!')
            return
    
        crv_name_list = []
        for i in range(num_children):
            
            child = root.child(i)
            
            if child.checkState():
                
                crv_name_list.append(child.text())
                

        rig_name = self.name_line_edit.text()
        name_start_index = self.name_start_index_spinbox.value()
        cable_radius = self.cable_radius_spinbox.value()
        cable_ik_joints = self.cable_ik_joints_spinbox.value()
        cable_bind_joints = self.cable_bind_joints_spinbox.value()           
        use_existing_hairsystem = self.use_existing_group_box.isChecked()
        share_hairsystem = self.share_hairsystem_checkbox.isChecked()
        mesh_set_unicode = self.mesh_set_lineedit.text()
        start_ctrl_set_unicode = self.start_ctrl_set_lineedit.text()
        end_ctrl_set_unicode = self.end_ctrl_set_lineedit.text()
        follicle_set_unicode = self.follicle_set_lineedit.text()
        
        print(  crv_name_list,
                rig_name,
                name_start_index,
                cable_radius,
                cable_ik_joints,
                cable_bind_joints,
                mesh_set_unicode,
                start_ctrl_set_unicode,
                end_ctrl_set_unicode,
                follicle_set_unicode,
                use_existing_hairsystem,
                share_hairsystem)

        
        



def show():      
    win = CableSetupWidget(parent=maya_main_window())
    win.show()
    



try:
    win.close()
    
except NameError:
    print('No win to close')

win = CableSetupWidget(parent=maya_main_window())
win.show()


win.move(100,150)



'''
pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/tendril_design_v005_script_base.mb', f=True)

node = pm.PyNode('rig_ref')
pm.select(node)
win.add_joint_ref_click()
win.add_joint_ref_click()
'''