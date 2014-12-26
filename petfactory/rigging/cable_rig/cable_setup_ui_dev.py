from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
class CableSetupWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(CableSetupWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300,100)
        self.setWindowTitle("Cable Setup")
        
        
        # main vertical layout
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        # rig name
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
        self.tree_view.setAlternatingRowColors(True)
 
        
        self.tree_view.setModel(self.model)
        self.vertical_layout.addWidget(self.tree_view)
        
        self.model.setHorizontalHeaderLabels(['Ref curve', 'Name'])
        
        
        # add ref curve
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
        
        # hairsystem group box
        hairsystem_group_box = QtGui.QGroupBox("Hairsystem")
        self.vertical_layout.addWidget(hairsystem_group_box)
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
        
        self.num_joints_spinbox = CableSetupWidget.add_int_spinbox('Number of joints', self.vertical_layout)
        self.cable_radius_spinbox = CableSetupWidget.add_int_spinbox('Cable radius', self.vertical_layout)

        # Setup
        setup_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(setup_horiz_layout)
        
        self.setup_button = QtGui.QPushButton('Setup Cable')
        self.setup_button.setMinimumWidth(100)
        setup_horiz_layout.addStretch()
        setup_horiz_layout.addWidget(self.setup_button)
        self.setup_button.clicked.connect(self.setup_clicked)
        
    @staticmethod
    def add_int_spinbox(label, parent_layout):
        
        horiz_layout = QtGui.QHBoxLayout()
        parent_layout.addLayout(horiz_layout)

        label = QtGui.QLabel(label)
        label.setMinimumWidth(100)
        horiz_layout.addWidget(label)
        
        horiz_layout.addStretch()
         
        spinbox = QtGui.QSpinBox()
        horiz_layout.addWidget(spinbox)
        spinbox.setMinimumWidth(100)
        
        return spinbox
            
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
    
       
    def setup_clicked(self):
        
        ref_crv_list = []
        
        
        
        num_children = self.model.rowCount()
        share_hairsystem = self.share_hairsystem_checkbox.isChecked()
        use_existing = self.use_existing_group_box.isChecked()
        existing_hairsystem = self.existing_hairsystem_line_edit.text()
        
        num_joints = self.num_joints_spinbox.value()
        cable_radius = self.cable_radius_spinbox.value()
    
        root = self.model.invisibleRootItem()
        for i in range(num_children):
            
            child = root.child(i)
            
            if child.checkState():
                
                ref_crv_list.append(child.text())
                

        name = self.name_line_edit.text()
        
        
        print(ref_crv_list, name, share_hairsystem, use_existing, existing_hairsystem, num_joints, cable_radius)
            

def show():      
    win = CableSetupWidget(parent=maya_main_window())
    win.show()
    

pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/3deg_5cvs.mb', f=True)

pm.select('curve0')
try:
    win.close()
    
except NameError:
    print('No win to close')

win = CableSetupWidget(parent=maya_main_window())
win.show()

win.add_joint_ref_click()

win.move(100,250)


