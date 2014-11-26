from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
from PySide import QtCore, QtGui
import random


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
class Toggle_viz(QtGui.QWidget):

    def __init__(self, obj_a, obj_b, parent=None):
        super(Toggle_viz, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.toggle_enum = 0
        
        self.obj_a = obj_a
        self.obj_b = obj_b

        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        self.toggle_button = QtGui.QPushButton('Toggle')
        self.toggle_button.setFixedSize(100,100)
        self.vertical_layout.addWidget(self.toggle_button)
        self.toggle_button.clicked.connect(self.toggle_button_click)
        
    def toggle_button_click(self):
        
        mods = QtGui.QApplication.keyboardModifiers()
        
    	if mods & QtCore.Qt.ShiftModifier:
    	    #print('shift')
    	    pm.warning('Hide both objects')
    	    self.obj_a.visibility.set(False)
            self.obj_b.visibility.set(False)
    	    return
        
        # cmd (mac) or ctrl (win)
        if mods & QtCore.Qt.ControlModifier:
            pm.warning('Hide both objects')
    	    self.obj_a.visibility.set(self.toggle_enum)
            self.obj_b.visibility.set(self.toggle_enum)
            self.toggle_enum = not self.toggle_enum
    	    return
    	    
    	if mods & QtCore.Qt.AltModifier:
    	    return
	
        self.obj_a.visibility.set(self.toggle_enum)
        self.toggle_enum = not self.toggle_enum
        self.obj_b.visibility.set(self.toggle_enum)


sel_list = pm.ls(sl=True)

if len(sel_list) < 2:
    pm.warning('Please select two transform')

else:
        
    if not isinstance(sel_list[0], pm.nodetypes.Transform) or not isinstance(sel_list[1], pm.nodetypes.Transform):
        pm.warning('Please select a NurbsCurve transform')
        
    else:
        win = Toggle_viz(sel_list[0], sel_list[1], parent=maya_main_window())
        win.show()