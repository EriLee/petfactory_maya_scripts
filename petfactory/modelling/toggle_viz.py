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
        
        self.obj_a_visible = False
        self.obj_hidden = False
        
        self.obj_a = obj_a
        self.obj_b = obj_b

        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        self.toggle_button = QtGui.QPushButton('A')
        self.toggle_button.setFixedSize(100,100)
        self.vertical_layout.addWidget(self.toggle_button)
        self.toggle_button.clicked.connect(self.toggle_button_click)


    def toggle_button_click(self):
        
        mods = QtGui.QApplication.keyboardModifiers()
        
        if mods & QtCore.Qt.ShiftModifier:
            #print('shift')
            #pm.warning('Hide both objects')
            
            if self.obj_hidden:
                self.obj_a.visibility.set(True)
                self.obj_b.visibility.set(True)
                self.obj_hidden = False
                self.toggle_button.setText('A B')
                
            else:
                self.obj_a.visibility.set(False)
                self.obj_b.visibility.set(False)
                self.obj_hidden = True
                self.toggle_button.setText('. .')
                
            return
        
        # cmd (mac) or ctrl (win)
        if mods & QtCore.Qt.ControlModifier:
            return
            
        if mods & QtCore.Qt.AltModifier:
            obj = Toggle_viz.list_objects()
            self.obj_a = obj[0]
            self.obj_b = obj[1]
            return

        # no modifiers
        self.obj_a.visibility.set(self.obj_a_visible)
        btn_text = 'A' if self.obj_a_visible else 'B'
        self.obj_a_visible = not self.obj_a_visible
        self.obj_b.visibility.set(self.obj_a_visible)
        self.obj_hidden = False
        self.toggle_button.setText(btn_text)


    @staticmethod
    def list_objects():
        
        sel_list = pm.ls(sl=True)
        
        if len(sel_list) < 2:
            pm.warning('Please select two transform')
            return None
        
        else:
                
            if not isinstance(sel_list[0], pm.nodetypes.Transform) or not isinstance(sel_list[1], pm.nodetypes.Transform):
                pm.warning('Please select a NurbsCurve transform')
                return None
                
            else:
                return (sel_list[0], sel_list[1])


obj = Toggle_viz.list_objects()

if obj:
    win = Toggle_viz(obj[0], obj[1], parent=maya_main_window())
    win.show()