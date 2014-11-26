from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
from PySide import QtCore, QtGui
import random


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
# the main ui class  
class Curve_spreadsheet(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(Curve_spreadsheet, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        
        self.curve = None
        
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        
        self.path_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.path_horiz_layout)

        self.path_label = QtGui.QLabel('Select Path')
        self.path_horiz_layout.addWidget(self.path_label)
        
        self.path_line_edit = QtGui.QLineEdit()
        self.path_horiz_layout.addWidget(self.path_line_edit)
        
        self.add_path_button = QtGui.QPushButton('Add Path')
        self.path_horiz_layout.addWidget(self.add_path_button)
        self.add_path_button.clicked.connect(self.add_path_click)
        
        
        self.table_view = QtGui.QTableView()
        self.vertical_layout.addWidget(self.table_view)
        
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Inner Radius', 'Outer Radius'])
  
        self.table_view.setModel(self.model)
        
        #v_header = self.table_view.verticalHeader()
        h_header = self.table_view.horizontalHeader()
        h_header.setResizeMode(QtGui.QHeaderView.Stretch)
        
        
        self.build_button = QtGui.QPushButton('Build it!')
        self.vertical_layout.addWidget(self.build_button)
        self.build_button.clicked.connect(self.on_build_click)
    
    def add_path_click(self):
        
        self.model.clear()
        
        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a NurbsCurve transform')
            return
        
        if not isinstance(sel_list[0], pm.nodetypes.Transform):
            pm.warning('Please select a NurbsCurve transform')
            return
        
        try:
            crv = sel_list[0].getShape()
            
        except:
            pm.warning('Please select a NurbsCurve transform')
            return

        
        self.curve = crv     
        crv_name = crv.longName()
            
            
        self.path_line_edit.setText(crv_name)
        
        #num_corners = 5
        #num_corners = random.randint(1, 10)
        
        cv_list = crv.getCVs(space='world')
        num_cvs = len(cv_list)
        num_corners = num_cvs -2
        
        if num_corners < 1:
            pm.warning('Please select a degree1 curve with more than 2 CVs')
            
        
        inner = '1'
        outer = '2'
        
        
        for row in range(num_corners):
            
            item_inner = QtGui.QStandardItem(inner)
            item_outer = QtGui.QStandardItem(outer)
            
            self.model.setItem(row, 0, item_inner);
            self.model.setItem(row, 1, item_outer);
        
        
        
    def on_build_click(self):
        
        num_rows = self.model.rowCount()
        
        for row in range(num_rows):
            
            inner_radius_text = self.model.item(row,0).text()
            outer_radius_text = self.model.item(row,1).text()
            
            try:
                inner_radius = float(inner_radius_text)
                
            except ValueError as e:
                pm.warning('The Inner Radius of row {0} is not a valid number'.format(row+1))
                #print(e)
                return None
                
            try:
                outer_radius = float(outer_radius_text)
                
            except ValueError as e:
                pm.warning('The Outer Radius of row {0} is not a valid number'.format(row+1))
                #print(e)
                return None
            
            print('Row {0}'.format(row))
            print('Inner radius: {0}'.format(inner_radius_text))
            print('Outer radius: {0}'.format(outer_radius_text))
        


        
win = Curve_spreadsheet(parent=maya_main_window())
win.show()