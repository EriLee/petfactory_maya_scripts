from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial


'''

TODO

Instead of using tab to toggle tool use qwerety

maybe use q to inc toggle ?


'''
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class SpinboxWidget(QtGui.QWidget):
    
    def __init__(self, label=None, min=None, max=None, default=None, double_spinbox=False):   
       
        super(SpinboxWidget, self).__init__()
        
        hbox = QtGui.QHBoxLayout()
        self.setLayout(hbox)
        
        if label is not None:
            self.label = QtGui.QLabel(label)
            #self.label.setMinimumWidth(80)
            hbox.addWidget(self.label)
            hbox.addStretch()
         
        self.spinbox = QtGui.QSpinBox() if not double_spinbox else QtGui.QDoubleSpinBox()
        self.spinbox.setMinimumWidth(100)
        
        if min:
            self.spinbox.setMinimum(min)
        if max:
            self.spinbox.setMaximum(max)
        if default:
            self.spinbox.setValue(default)
            
        hbox.addWidget(self.spinbox)
        
    def get_spinbox():
        return self.spinbox
        
    def get_value(self):
        return self.spinbox.value()
        
                
class ComboboxWidget(QtGui.QWidget):
    
    def __init__(self, items, label=None):   
       
        super(ComboboxWidget, self).__init__()
        
        hbox = QtGui.QHBoxLayout()
        self.setLayout(hbox)
        self.items = items
        
        if label is not None:
            self.label = QtGui.QLabel(label)
            hbox.addWidget(self.label)
        
        self.combobox = QtGui.QComboBox()
        self.combobox.addItems(items)
        hbox.addWidget(self.combobox)
        self.combobox.setFocusPolicy(QtCore.Qt.NoFocus)
        #self.combobox.currentIndexChanged.connect(self.update_index)
        
    #def update_index(self):
        #pass
        
    def inc_selection(self):
        
        index = self.combobox.currentIndex() + 1
        if index > len(self.items)-1:
            index = 0
            
        self.combobox.setCurrentIndex(index)
    
    def set_selection(self, index):
         if index > len(self.items)-1:
             pm.warning('index out of bounds, max index is {0}'.format(len(self.items)-1))
             return
             
         self.combobox.setCurrentIndex(index)
            
    def get_selected_text(self):
        return(self.combobox.itemText(self.combobox.currentIndex()))
    
    def get_selected_index(self):
        return self.combobox.currentIndex()

        
        
                
        
        
class RadioButtonGroup(QtGui.QGroupBox):
    
    def __init__(self, title, items):   
       
        super(RadioButtonGroup, self).__init__()
        
        self.setTitle(title)
        self.curr_sel_index = 0
        
        hbox = QtGui.QHBoxLayout()
        
        self.radiobutton_list = []
        for item in items:
            rb = QtGui.QRadioButton(item)
            self.radiobutton_list.append(rb)
            hbox.addWidget(rb)
            
            
        self.radiobutton_list[self.curr_sel_index].setChecked(True)

        hbox.addStretch(1)
        self.setLayout(hbox)
    
    def get_selected_text(self):
        
        for rb in self.radiobutton_list:
            
            if rb.isChecked():
                return(rb.text())
    
    def get_selected_index(self):
        
        for index, rb in enumerate(self.radiobutton_list):
            
            if rb.isChecked():
                return(index)
                
    
    def inc_selection(self):
        self.radiobutton_list[self.curr_sel_index].setChecked(False)
        
        
        self.curr_sel_index += 1
        if self.curr_sel_index > len(self.radiobutton_list)-1:
            self.curr_sel_index = 0
        
        self.radiobutton_list[self.curr_sel_index].setChecked(True)
        

    def dec_selection(self):
        self.radiobutton_list[self.curr_sel_index].setChecked(False)
        
        
        self.curr_sel_index -= 1
        if self.curr_sel_index < 0:
            self.curr_sel_index = len(self.radiobutton_list)-1
        
        self.radiobutton_list[self.curr_sel_index].setChecked(True)    
        
        
        

# the main ui class  
class NudgeTransform(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(NudgeTransform, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(150, 200)
        self.setWindowTitle("Nudge transform")
        
        
        # set to false if we do not want to toggle the gui button on keypress
        #self.set_button_down_on_keypress = True
        self.button_dict = {}
        
        # layout
        vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(vertical_layout)
        
        self.axis_radiogroup = RadioButtonGroup(title='Axis', items=['x', 'y', 'z'])
        vertical_layout.addWidget(self.axis_radiogroup)
                
        self.tool_combobox = ComboboxWidget(label='Tool', items=['Translate', 'Rotate', 'Scale'])
        vertical_layout.addWidget(self.tool_combobox)
        
        
        self.step_small_spinbox = SpinboxWidget(label='Step small', default=.1, double_spinbox=True)
        vertical_layout.addWidget(self.step_small_spinbox)
        
        self.step_big_spinbox = SpinboxWidget(label='Step big', default=5, double_spinbox=True)
        vertical_layout.addWidget(self.step_big_spinbox)
        
        
        vertical_layout.addStretch()
        
        
        hbox = QtGui.QHBoxLayout()
        vertical_layout.addLayout(hbox)
        
        self.left_button = QtGui.QPushButton(' - ')
        self.left_button.clicked.connect(partial(self.on_click, 'down'))
        hbox.addWidget(self.left_button)
        self.button_dict[QtCore.Qt.Key_Down] = self.left_button
        
        
        self.right_button = QtGui.QPushButton(' + ')
        self.right_button.clicked.connect(partial(self.on_click, 'up'))
        hbox.addWidget(self.right_button)
        self.button_dict[QtCore.Qt.Key_Up] = self.right_button
        
        
        
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFocus()
          
        
    # handle keypress
    def keyPressEvent(self, event):
        
        key = event.key()
        
        modifier = QtCore.Qt.Key_Shift if event.modifiers() & QtCore.Qt.SHIFT else None

     
        #if self.set_button_down_on_keypress:
            
        button = self.button_dict.get(key)
            
        if button:
            button.setDown(True)
        
        # set key
        if key == QtCore.Qt.Key_S:
            #print('Key_S')
            pass
            
        # step time forward
        elif key == QtCore.Qt.Key_Right:
            #print('Key_Right')
            pass
                            
        # step time back    
        elif key == QtCore.Qt.Key_Left:
            #print('Key_Left')
            pass            
            
        # increment
        elif key == QtCore.Qt.Key_Up:
            #print('Key_Up')
            self.do_transform('up', modifier)

        # deccrement    
        elif key == QtCore.Qt.Key_Down:
            #print('Key_Down')
            self.do_transform('down', modifier)
            
        # toggle axis
        elif key == QtCore.Qt.Key_Space:
            #print('Key_Space')
            self.axis_radiogroup.inc_selection()
            
        # toggle translate tool, move, rotate, scale
        elif key == QtCore.Qt.Key_Q:
            self.tool_combobox.inc_selection()
        
        # toggle translate tool, move, rotate, scale
        elif key == QtCore.Qt.Key_W:
            self.tool_combobox.set_selection(0)
            
        elif key == QtCore.Qt.Key_E:
            self.tool_combobox.set_selection(1)
        
        elif key == QtCore.Qt.Key_R:
            self.tool_combobox.set_selection(2)
        
    def do_transform(self, dir, modifier=None):
    
        #print(modifier)
        
        tool = self.tool_combobox.get_selected_text().lower()
        
        small_amount = self.step_small_spinbox.get_value()
        big_amount = self.step_big_spinbox.get_value()
        
        if modifier is None:
            amount = small_amount
        else:
            amount = big_amount
            
            
        if dir == 'down':
            amount = amount*-1
              
        axis = self.axis_radiogroup.get_selected_text()
        

        if axis == 'x':
            vec = (amount, 0, 0)
        elif axis == 'y':
            vec = (0, amount, 0)
        else:
            vec = (0, 0, amount)

        
        sel_list = pm.ls(sl=True)
        if sel_list:
            sel = sel_list[0]
        else:
            return
  
        if sel:
            
            if tool == 'translate':
                pm.xform(translation=vec, relative=True, objectSpace=True)
                
            elif tool == 'rotate':
                pm.xform(ro=vec, relative=True, objectSpace=True)
                
            elif tool == 'scale':
                pm.xform(scale=sel.scale.get()+amount)
                
        
    def on_click(self, dir):
        
        modifier = None
        
        q_modifier = QtGui.QApplication.keyboardModifiers()
        
        if q_modifier == QtCore.Qt.ShiftModifier:
            modifier = QtCore.Qt.Key_Shift
            
        self.do_transform(dir, modifier=modifier)
        
                            
    def keyReleaseEvent(self, event):
        
        key = event.key()
        
        #if self.set_button_down_on_keypress:
            
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

