from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
import maya.cmds as cmds
from functools import partial


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    

# the main ui class  
class FilterViewObjects(QtGui.QWidget):

    def __init__(self, parent=None):
        
        self.all_hidden = False
        
        super(FilterViewObjects, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(120, 120)
        self.setWindowTitle("Set Drawing Overide")
        
        # layout
        vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(vertical_layout)
        vertical_layout.setContentsMargins(2,2,2,2)

        
        FilterViewObjects.create_button('Hide all', vertical_layout, partial(self.set_visibility, False))
        FilterViewObjects.create_button('Show all', vertical_layout, partial(self.set_visibility, True))
        FilterViewObjects.create_button('Poly, Img, Curves', vertical_layout, self.show_polygons)

        
    @staticmethod
    def create_button(label, layout, callback):
        
        btn = QtGui.QPushButton(label)
        btn.setFixedSize(120,40)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        
           
    def toggle_all(self):
        
        self.all_hidden = not self.all_hidden
        set_visibility(self.all_hidden)
            
    def set_visibility(self, value):
        
        panel = pm.getPanel(wf=1)

        try:
            pm.modelEditor(panel, e=True, allObjects=value)
            
        except RuntimeError as e:
            pass
            #print(e)
            
    
    def show_polygons(self):
        
        panel = pm.getPanel(wf=1)

        try:
            pm.modelEditor(panel, e=True, allObjects=0)
            pm.modelEditor(panel, e=True, polymeshes=True)
            pm.modelEditor(panel, e=True, imagePlane=True)
            pm.modelEditor(panel, e=True, nurbsCurves=True)
   
            
        except RuntimeError as e:
            #print(e)
            pass
        


def show():      
    win = FilterViewObjects(parent=maya_main_window())
    win.show()
'''   
try:
    win.close()
    
except NameError as e:
    print(e)
    
win = FilterViewObjects(parent=maya_main_window())
win.move(100, 210)
win.show()
'''