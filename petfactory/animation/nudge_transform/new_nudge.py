from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


# the main ui class  
class NudgeTransform(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(NudgeTransform, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(150, 200)
        self.setWindowTitle("Nudge transform")
        
        
    # handle keypress
    def keyPressEvent(self, event):
        
        # set key
        if event.key() == QtCore.Qt.Key_S:
            print('Key_S')
            
        # step time forward
        elif event.key() == QtCore.Qt.Key_Right:
            print('Key_Right')
        
        # step time back    
        elif event.key() == QtCore.Qt.Key_Left:
            print('Key_Left')
            
        # increment
        elif event.key() == QtCore.Qt.Key_Up:
            print('Key_Up')
        
        # deccrement    
        elif event.key() == QtCore.Qt.Key_Down:
            print('Key_Down')
            
        # toggle axis
        elif event.key() == QtCore.Qt.Key_Space:
            print('Key_Space')
            
        # toggle translate tool, move, rotate, scale
        elif event.key() == QtCore.Qt.Key_Tab:
            print('Key_Tab')
                    

        
def show():      
    win = Curve_spreadsheet(parent=maya_main_window())
    win.show()

try:
    win.close()
except NameError as e:
    print(e)
    
win = NudgeTransform(parent=maya_main_window())
win.move(100, 210)
win.show()

