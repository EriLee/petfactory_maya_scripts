from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
from PySide import QtCore, QtGui
import random


def create_round_corners(crv, radius_list=None, inner_radius=.5, outer_radius=1, name='round_corner_curve'):
    

    #cv_list = crv.getShape().getCVs(space='world')
    cv_list = crv.getCVs(space='world')
    num_cv = len(cv_list)
    crv_cv_list = []
    
    uniform_radius = True
    
    if radius_list:
        if len(radius_list) != num_cv-2:
            pm.warning('The length of radius list ({0}) is not matching the number of corners({1})!'.format(len(radius_list), num_cv-2))
        else:
            uniform_radius = False

    
    for index, cv in enumerate(cv_list):
        
        if index is 0:
                lin_start_pos = cv_list[index]
                
        if index < num_cv-2:
            
            if not uniform_radius:
                pos_a = ((cv_list[index] - cv_list[index+1]).normal())*radius_list[index][1] + cv_list[index+1]
                pos_b = ((cv_list[index] - cv_list[index+1]).normal())*radius_list[index][0] + cv_list[index+1]
                pos_c = ((cv_list[index+2] - cv_list[index+1]).normal())*radius_list[index][0] + cv_list[index+1]
                pos_d = ((cv_list[index+2] - cv_list[index+1]).normal())*radius_list[index][1] + cv_list[index+1]

            else:
                pos_a = ((cv_list[index] - cv_list[index+1]).normal())*outer_radius + cv_list[index+1]
                pos_b = ((cv_list[index] - cv_list[index+1]).normal())*inner_radius + cv_list[index+1]
                pos_c = ((cv_list[index+2] - cv_list[index+1]).normal())*inner_radius + cv_list[index+1]
                pos_d = ((cv_list[index+2] - cv_list[index+1]).normal())*outer_radius + cv_list[index+1]

            #create_loc(pos_a)
            #create_loc(pos_b)
            #create_loc(pos_c)
            #create_loc(pos_d)
            
            pos_list = (    #[pos_a[0], pos_a[1], pos_a[2]],
                            [pos_b[0], pos_b[1], pos_b[2]],
                            [pos_c[0], pos_c[1], pos_c[2]],
                            #[pos_d[0], pos_d[1], pos_d[2]],
            )
            
            pos_deg_1 = (    [lin_start_pos[0], lin_start_pos[1], lin_start_pos[2]],
                              [pos_a[0], pos_a[1], pos_a[2]]
            )
            
            # deg 1
            crv_cv_list.append(pos_deg_1)
            
            # deg 3
            crv_cv_list.append(pos_list)    
                
            lin_start_pos = pos_d
            
        elif index < num_cv-1:
            
            pos_deg_1 = (    [lin_start_pos[0], lin_start_pos[1], lin_start_pos[2]],
                              [cv_list[index+1][0], cv_list[index+1][1], cv_list[index+1][2]]
            )
            
            # deg 1
            crv_cv_list.append(pos_deg_1)
            
    return crv_cv_list
    
  

#crv_cv_list = create_round_corners(crv, radius_list=[(.5,1),(1,2),(1,2),(.5,1),(2,4),(.5,1),(.75,3),(.5,1)])

#pos_list = []
#for crv_cv in crv_cv_list:
#    for pos in crv_cv:
#        pos_list.append(pos)
   


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
        
        pos_list = []
        radius_list = []
        
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
            
            radius_list.append((inner_radius, outer_radius))
            #print('Row {0}'.format(row))
            #print('Inner radius: {0}'.format(inner_radius_text))
            #print('Outer radius: {0}'.format(outer_radius_text))
            
        
        crv_cv_list = create_round_corners(self.curve, radius_list=radius_list)
        
        pos_list = []
        for crv_cv in crv_cv_list:
            for pos in crv_cv:
                pos_list.append(pos)
        
        pm.curve(degree=3, p=pos_list, name="smooth")


        


        
win = Curve_spreadsheet(parent=maya_main_window())
win.show()