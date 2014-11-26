from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
from PySide import QtCore, QtGui


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
# the main ui class  
class Curve_spreadsheet(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(Curve_spreadsheet, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        self.table_view = QtGui.QTableView()
        self.vertical_layout.addWidget(self.table_view)
        
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Inner Radius', 'Outer Radius'])
        
        num_corners = 5
        inner = '1'
        outer = '2'
        
        for row in range(num_corners):
            
            item_inner = QtGui.QStandardItem(inner)
            item_outer = QtGui.QStandardItem(outer)
            
            self.model.setItem(row, 0, item_inner);
            self.model.setItem(row, 1, item_outer);
        
        self.table_view.setModel(self.model)
        
        #v_header = self.table_view.verticalHeader()
        h_header = self.table_view.horizontalHeader()
        h_header.setResizeMode(QtGui.QHeaderView.Stretch)
        
        self.build_button = QtGui.QPushButton('Build it!')
        self.vertical_layout.addWidget(self.build_button)
        self.build_button.clicked.connect(self.on_build_click)
        
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