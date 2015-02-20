from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm



def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    

# the main ui class  
class AddVrayAttrs(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(AddVrayAttrs, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300, 350)
        self.setWindowTitle("Add V-Ray attributes")
                
        vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(vertical_layout)
        
        # use existing hairsystem group box
        self.subdivision_groupbox = QtGui.QGroupBox("Subdivision")
        vertical_layout.addWidget(self.subdivision_groupbox)
        self.subdivision_groupbox.setCheckable(True)
        
        subdivision_groupbox_vert_layout = QtGui.QVBoxLayout()
        self.subdivision_groupbox.setLayout(subdivision_groupbox_vert_layout)
        self.subdivide_uvs_checkbox = AddVrayAttrs.add_checkbox(label='Subdivide UVs', layout=subdivision_groupbox_vert_layout)
        
        # use existing hairsystem group box
        self.subdivision_disp_quality_groupbox = QtGui.QGroupBox("Subdivision and diplacement quality")
        vertical_layout.addWidget(self.subdivision_disp_quality_groupbox)
        self.subdivision_disp_quality_groupbox.setCheckable(True)
        subdivision_disp_quality_groupbox_vert_layout = QtGui.QVBoxLayout()
        self.subdivision_disp_quality_groupbox.setLayout(subdivision_disp_quality_groupbox_vert_layout)
        
        self.edge_length_add_spinbox = AddVrayAttrs.add_spinbox(label='Edge length', min=.1, layout=subdivision_disp_quality_groupbox_vert_layout, default=4, double_spinbox=True)
        self.max_subdivs_spinbox = AddVrayAttrs.add_spinbox(label='Max subdivs', min=1, layout=subdivision_disp_quality_groupbox_vert_layout, default=64)
        
        
        # use existing hairsystem group box
        self.displacement_control_groupbox = QtGui.QGroupBox("displacement control")
        vertical_layout.addWidget(self.displacement_control_groupbox)
        self.displacement_control_groupbox.setCheckable(True)
        displacement_control_groupbox_vert_layout = QtGui.QVBoxLayout()
        self.displacement_control_groupbox.setLayout(displacement_control_groupbox_vert_layout)
        
        self.displacement_amount_spinbox = AddVrayAttrs.add_spinbox(label='Displacement amount', min=.1, layout=displacement_control_groupbox_vert_layout, default=1, double_spinbox=True)

        
        vertical_layout.addStretch()
        
        self.add_attr_button = QtGui.QPushButton('Add attrs')
        vertical_layout .addWidget(self.add_attr_button)
        self.add_attr_button.clicked.connect(self.add_attr_button_clicked)
        

    @staticmethod
    def add_spinbox(label, layout, min=None, max=None, default=None, double_spinbox=False):
        
        horiz_layout = QtGui.QHBoxLayout()
        layout.addLayout(horiz_layout)

        label = QtGui.QLabel(label)
        label.setMinimumWidth(100)
        horiz_layout.addWidget(label)
        
        horiz_layout.addStretch()
         
        spinbox = QtGui.QSpinBox() if not double_spinbox else QtGui.QDoubleSpinBox()
        if min:
            spinbox.setMinimum(min)
        if max:
            spinbox.setMaximum(max)
        if default:
            spinbox.setValue(default)
            
        horiz_layout.addWidget(spinbox)
        spinbox.setMinimumWidth(100)
        
        return spinbox
        
    @staticmethod
    def add_checkbox(label, layout, enabled=True):
        
        horiz_layout = QtGui.QHBoxLayout()
        layout.addLayout(horiz_layout)

        checkbox = QtGui.QCheckBox()    
        horiz_layout.addWidget(checkbox)
        
        checkbox.setChecked(False)
        label = QtGui.QLabel(label)
        label.setMinimumWidth(100)
        horiz_layout.addWidget(label)
 
        horiz_layout.addStretch()
  
        return checkbox
        
        
    def add_attr_button_clicked(self):
        
        
        sel_list = pm.ls(sl=True)
    
        mesh_list = []
        
        for sel in sel_list:
            
            try:
                mesh = sel.getShape()
                if not isinstance(mesh, pm.nodetypes.Mesh):
                    pm.warning('Not a polygon mesh, skipping')
                    continue
                    
            except AttributeError as e:
                print('Not a polygon mesh, skipping', e)
                continue
            
            mesh_list.append(sel.getShape())
                
            
        #print(mesh_list)
            
        use_subdivision = self.subdivision_groupbox.isChecked()
        use_subdivision_disp_quality = self.subdivision_disp_quality_groupbox.isChecked()
        use_displacement_control_groupbox = self.displacement_control_groupbox.isChecked()
        
        #print(use_subdivision, use_subdivision_disp_quality, use_displacement_control_groupbox)
        
        
        for mesh in mesh_list:
            
            if use_subdivision:
                pm.vray("addAttributesFromGroup", mesh.longName(), "vray_subdivision", 1)
                mesh.vraySubdivUVs.set(self.subdivide_uvs_checkbox.isChecked())
                 
            else:
                pm.vray("addAttributesFromGroup", mesh.longName(), "vray_subdivision", 0)
                
                
                
            if use_subdivision_disp_quality:
                pm.vray("addAttributesFromGroup", mesh.longName(), "vray_subquality", 1)
                mesh.vrayEdgeLength.set(self.edge_length_add_spinbox.value())
                mesh.vrayMaxSubdivs.set(self.max_subdivs_spinbox.value())
                
                
        
        
                
            else:
                pm.vray("addAttributesFromGroup", mesh.longName(), "vray_subquality", 0)
                
                
                
            if use_displacement_control_groupbox:
                
                pm.vray("addAttributesFromGroup", mesh.longName(), "vray_displacement", 1)
                mesh.vrayDisplacementAmount.set(self.displacement_amount_spinbox.value())
                mesh.vrayDisplacementKeepContinuity.set(True)
                
            else:
                pm.vray("addAttributesFromGroup", mesh.longName(), "vray_displacement", 0)
                
            
        
       
        

def show():      
    win = AddVrayAttrs(parent=maya_main_window())
    win.show()
    return win

'''
try:
    win.close()
    
except NameError:
    pass
    
win = show()
win.move(150,250)
'''