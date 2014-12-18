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
        
        self.resize(150, 150)
        self.setWindowTitle("Pipe Tool")
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(1)
        

        num_buttons = 32
        btn_per_row = 8

        for n in range(num_buttons):
            
            color = QtGui.QColor(125, 0, 0)
            pixmap = QtGui.QPixmap(50, 50)
            pixmap.fill(QtGui.QColor(color))
            icon = QtGui.QIcon(pixmap)
            
            
            button = QtGui.QPushButton(icon, "")
            #button.setAutoFillBackground(True)
            
            button.setMinimumSize(50,50)
            button.setMaximumSize(50,50)
            button.setIconSize(QtCore.QSize(50,50))
            button.color_index = n
            button.clicked.connect(self.set_override)
            grid.addWidget(button, n/btn_per_row, n%btn_per_row)
            


        self.setLayout(grid)
        grid.setContentsMargins(2,2,2,2)
        
    def set_override(self):
        
        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('no selection')
            return
        
        for sel in sel_list:
            shape = sel.getShape()
            index = self.sender().color_index
            shape.overrideColor.set(index)
            print('color index set to: \n{0}'.format(index))


def show():      
    win = Curve_spreadsheet(parent=maya_main_window())
    win.show()
    
    
show()