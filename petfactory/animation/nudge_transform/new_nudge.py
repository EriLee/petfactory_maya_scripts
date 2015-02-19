from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial

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
        
        self.set_button_down_on_keypress = True
        self.button_dict = {}
        
        # layout
        vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(vertical_layout)
        
        self.right_button = QtGui.QPushButton('>>')
        self.right_button.clicked.connect(partial(self.on_click, 'right'))
        vertical_layout.addWidget(self.right_button)
        self.button_dict[QtCore.Qt.Key_Right] = self.right_button
        
        self.left_button = QtGui.QPushButton('<<')
        self.left_button.clicked.connect(partial(self.on_click, 'left'))
        vertical_layout.addWidget(self.left_button)
        self.button_dict[QtCore.Qt.Key_Left] = self.left_button
          
        
    # handle keypress
    def keyPressEvent(self, event):
        
        key = event.key()
        
        if self.set_button_down_on_keypress:
            
            button = self.button_dict.get(key)
            
            if button:
                button.setDown(True)
        
        # set key
        if key == QtCore.Qt.Key_S:
            print('Key_S')
            
        # step time forward
        elif key == QtCore.Qt.Key_Right:
            print('Key_Right')
            self.on_click('right')
                
        # step time back    
        elif key == QtCore.Qt.Key_Left:
            print('Key_Left')
            self.on_click('left')
            
        # increment
        elif key == QtCore.Qt.Key_Up:
            print('Key_Up')
        
        # deccrement    
        elif key == QtCore.Qt.Key_Down:
            print('Key_Down')
            
        # toggle axis
        elif key == QtCore.Qt.Key_Space:
            print('Key_Space')
            
            
        # toggle translate tool, move, rotate, scale
        elif key == QtCore.Qt.Key_Tab:
            print('Key_Tab')
            
    def on_click(self, dir):
        
        sel_list = pm.ls(sl=True)
        if sel_list:
            sel = sel_list[0]
        else:
            return
  
        if sel:
            
            if dir == 'left':
                sel.translateBy((0,.1,0))
                
            elif dir == 'right':
                sel.translateBy((0,-.1,0))
                
    
                    
    def keyReleaseEvent(self, event):
        
        key = event.key()
        
        if self.set_button_down_on_keypress:
            
            button = self.button_dict.get(key)
            
            if button:
                button.setDown(False)
            

        
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

