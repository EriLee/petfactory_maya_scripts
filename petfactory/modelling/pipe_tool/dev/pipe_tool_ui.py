from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
# the main ui class  
class Curve_spreadsheet(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(Curve_spreadsheet, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300, 350)
        self.setWindowTitle("Pipe Tool")
                
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        

        # add path
        self.path_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.path_horiz_layout)
              
        self.add_path_button = QtGui.QPushButton('Add Path')
        self.add_path_button.setMinimumWidth(75)
        self.path_horiz_layout.addWidget(self.add_path_button)
        self.add_path_button.clicked.connect(self.add_path_click)
        
        self.path_line_edit = QtGui.QLineEdit()
        self.path_horiz_layout.addWidget(self.path_line_edit)
        
        # add mesh
        self.fitting_mesh_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.fitting_mesh_horiz_layout)
               
        self.add_fitting_mesh_button = QtGui.QPushButton('Add Mesh')
        self.add_fitting_mesh_button.setMinimumWidth(75)
        self.fitting_mesh_horiz_layout.addWidget(self.add_fitting_mesh_button)
        self.add_fitting_mesh_button.clicked.connect(self.add_fitting_mesh_click)
        
        self.fitting_mesh_line_edit = QtGui.QLineEdit()
        self.fitting_mesh_horiz_layout.addWidget(self.fitting_mesh_line_edit)
        
        
        # table view  
        self.table_view = QtGui.QTableView()
        self.vertical_layout.addWidget(self.table_view)
        
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Radius'])
  
        self.table_view.setModel(self.model)
        
        #v_header = self.table_view.verticalHeader()
        h_header = self.table_view.horizontalHeader()
        h_header.setResizeMode(QtGui.QHeaderView.Stretch)
           
        self.axis_div_spinbox = Curve_spreadsheet.add_int_spinbox('Axis Divisions', self.vertical_layout)
        self.length_div_spinbox = Curve_spreadsheet.add_int_spinbox('Length Divisions', self.vertical_layout)
        self.radial_div_spinbox = Curve_spreadsheet.add_int_spinbox('Radial Divisions', self.vertical_layout)
        
        # visualize
        '''
        self.visualize_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.visualize_horiz_layout)
        
        self.visualize_checkbox = QtGui.QCheckBox()
        self.visualize_horiz_layout.addWidget(self.visualize_checkbox)
        
        self.visualize_label = QtGui.QLabel('Visualize')
        self.visualize_horiz_layout.addWidget(self.visualize_label)
        self.visualize_horiz_layout.addStretch()
        '''
        
        
        # build button
        self.build_button_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.build_button_horiz_layout)
        
        self.build_button_horiz_layout.addStretch()
        self.build_button = QtGui.QPushButton('Build it!')
        self.build_button.setMinimumWidth(100)
        self.build_button_horiz_layout.addWidget(self.build_button)
        self.build_button.clicked.connect(self.on_build_click)
    
    
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

        
    def add_fitting_mesh_click(self):
        
        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a Mesh transform')
            return
        
        if not isinstance(sel_list[0], pm.nodetypes.Transform):
            pm.warning('Please select a Mesh transform')
            return
        
        try:
            mesh_shape = sel_list[0].getShape()

            if isinstance(mesh_shape, pm.nodetypes.Mesh):
                mesh_name = sel_list[0].longName() 
                
            else:
                pm.warning('Please select a Mesh transform')
                return
            
            
        except pm.general.MayaNodeError as e:
            pm.warning('Please select a Mesh transform', e)
            return
            
        self.fitting_mesh_line_edit.setText(mesh_name)
        
   
    
    def add_path_click(self):
        
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Radius'])
        
        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a NurbsCurve transform')
            return
        
        if not isinstance(sel_list[0], pm.nodetypes.Transform):
            pm.warning('Please select a NurbsCurve transform')
            return
        
        try:
            crv_shape = sel_list[0].getShape()
            
            if isinstance(crv_shape, pm.nodetypes.NurbsCurve):
                crv = sel_list[0]
                
            else:
                pm.warning('Please select a NurbsCurve transform')
                return
            
            
        except pm.general.MayaNodeError as e:
            pm.warning('Please select a NurbsCurve transform', e)
            return
  
        crv_name = crv.longName()    
        self.path_line_edit.setText(crv_name)
        
        cv_list = crv.getCVs(space='world')
        num_cvs = len(cv_list)
        num_corners = num_cvs -2
        
        if num_corners < 1:
            pm.warning('Please select a degree1 curve with more than 2 CVs')
            
        
        for row in range(num_corners):
            
            item_inner = QtGui.QStandardItem('1')

            self.model.setItem(row, 0, item_inner);
    
        
    def on_build_click(self):
        
        radius_list = []
        
        num_rows = self.model.rowCount()
        
        axis_divisions = self.axis_div_spinbox.value()
        length_divisions = self.length_div_spinbox.value()
        radial_divisions = self.radial_div_spinbox.value()
        
        crv = self.path_line_edit.text()
        fitting_mesh = self.fitting_mesh_line_edit.text()
        
        
        
        for row in range(num_rows):
            
            radius_text = self.model.item(row,0).text()
            
            try:
                radius = float(radius_text)
                
            except ValueError as e:
                pm.warning('The Inner Radius of row {0} is not a valid number'.format(row+1))
                #print(e)
                return None
                
            
            radius_list.append(radius)
            #print('Row {0}'.format(row))
            #print('Inner radius: {0}'.format(inner_radius_text))
            #print('Outer radius: {0}'.format(outer_radius_text))
            
        #print(radius_list)
        #visualize = self.visualize_checkbox.isChecked()
        #add_smooth_corners(self.curve, radius_list=radius_list, visualize=visualize)
        
        print(radius_list, axis_divisions, length_divisions, radial_divisions, fitting_mesh, crv)


def show():      
    win = Curve_spreadsheet(parent=maya_main_window())
    win.show()

try:
    win.close()
except NameError as e:
    print(e)
    
win = Curve_spreadsheet(parent=maya_main_window())
win.move(100, 210)
win.show()

