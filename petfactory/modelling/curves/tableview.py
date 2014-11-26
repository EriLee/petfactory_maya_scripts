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
        
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.setLayout(self.horizontalLayout)
        
        self.table_view = QtGui.QTableView()
        self.horizontalLayout.addWidget(self.table_view)
        
        self.model = QtGui.QStandardItemModel()
        
        num_corners = 5
        inner = '1'
        outer = '2'
        
        for row in range(num_corners):
            
            item_inner = QtGui.QStandardItem(inner)
            item_outer = QtGui.QStandardItem(outer)
            
            self.model.setItem(row, 0, item_inner);
            self.model.setItem(row, 1, item_outer);
        
        self.table_view.setModel(self.model)
        
        v_header = self.table_view.verticalHeader()
        h_header = self.table_view.horizontalHeader()
        h_header.setResizeMode(QtGui.QHeaderView.Stretch)
        #self.table_view.resizeColumnsToContents()

        
win = Curve_spreadsheet(parent=maya_main_window())
win.show()