from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
from functools import partial


'''

TODO



'''
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class SpinboxWidget(QtGui.QWidget):
    
    def __init__(self, label=None, min=None, max=None, default=None, double_spinbox=False):   
       
        super(SpinboxWidget, self).__init__()
        
        hbox = QtGui.QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)
        self.setLayout(hbox)
        
        
        if label is not None:
            self.label = QtGui.QLabel(label)
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
        hbox.setContentsMargins(0,0,0,0)
        self.setLayout(hbox)
        self.items = items
        
        if label is not None:
            self.label = QtGui.QLabel(label)
            hbox.addWidget(self.label)
            hbox.addStretch()
        
        self.combobox = QtGui.QComboBox()
        self.combobox.setMinimumWidth(100)
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
        
        
        change_value_hbox = QtGui.QHBoxLayout()
        vertical_layout.addLayout(change_value_hbox)
        
        self.minus_button = QtGui.QPushButton(' - ')
        self.minus_button.setFixedHeight(40)
        kargs = {'callback':'set_transform', 'dir':-1}
        self.minus_button.clicked.connect(partial(self.on_ui_click, **kargs))
        change_value_hbox.addWidget(self.minus_button)
        self.button_dict[QtCore.Qt.Key_Down] = self.minus_button
        
        
        self.plus_button = QtGui.QPushButton(' + ')
        self.plus_button.setFixedHeight(40)
        kargs = {'callback':'set_transform', 'dir':1}
        self.plus_button.clicked.connect(partial(self.on_ui_click, **kargs))        
        change_value_hbox.addWidget(self.plus_button)
        self.button_dict[QtCore.Qt.Key_Up] = self.plus_button
        
        
        self.time_step_spinbox = SpinboxWidget(label='Time step', default=5, min=0, max=999)
        vertical_layout.addWidget(self.time_step_spinbox)
        
        
        timeslider_hbox = QtGui.QHBoxLayout()
        vertical_layout.addLayout(timeslider_hbox)
        
        self.prev_time_button = QtGui.QPushButton(' < ')
        timeslider_hbox.addWidget(self.prev_time_button)
        self.button_dict[QtCore.Qt.Key_Left] = self.prev_time_button
        kargs = {'callback':'set_time', 'dir':-1}
        self.prev_time_button.clicked.connect(partial(self.on_ui_click, **kargs))
        
        self.set_keyframe_button = QtGui.QPushButton(' key ')
        self.set_keyframe_button.setFixedWidth(50)
        timeslider_hbox.addWidget(self.set_keyframe_button)
        self.button_dict[QtCore.Qt.Key_S] = self.set_keyframe_button
        kargs = {'callback':'set_keyframe'}
        self.set_keyframe_button.clicked.connect(partial(self.on_ui_click, **kargs))
        
        
        self.next_time_button = QtGui.QPushButton(' > ')
        timeslider_hbox.addWidget(self.next_time_button)
        self.button_dict[QtCore.Qt.Key_Right] = self.next_time_button
        kargs = {'callback':'set_time', 'dir':1}
        self.next_time_button.clicked.connect(partial(self.on_ui_click, **kargs))
        
        
        
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFocus()
          
        
    # handle keypress
    def keyPressEvent(self, event):
        
        key = event.key()
        
        modifier = None
        
        if event.modifiers() & QtCore.Qt.SHIFT:
            modifier = QtCore.Qt.Key_Shift
        elif event.modifiers() & QtCore.Qt.ALT:
            modifier = QtCore.Qt.Key_Alt
     
            
        button = self.button_dict.get(key)
            
        if button:
            button.setDown(True)
        
        # set key
        if key == QtCore.Qt.Key_S:
            #print('Key_S')
            self.set_keyframe(modifier=modifier)
            
        # step time forward
        elif key == QtCore.Qt.Key_Right:
            #print('Key_Right')
            self.set_time(dir=1, modifier=modifier)
                            
        # step time back    
        elif key == QtCore.Qt.Key_Left:
            #print('Key_Left')
            self.set_time(dir=-1, modifier=modifier)         
            
        # increment
        elif key == QtCore.Qt.Key_Up:
            #print('Key_Up')
            self.set_transform(dir=1, modifier=modifier)

        # deccrement    
        elif key == QtCore.Qt.Key_Down:
            #print('Key_Down')
            self.set_transform(dir=-1, modifier=modifier)
            
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

    def set_time(self, dir, modifier=None):
                
        if modifier is QtCore.Qt.Key.Key_Shift:
            pass
            
        elif modifier is QtCore.Qt.Key.Key_Alt:
            sel_list = pm.ls(sl=True)
            if sel_list:
                sel = sel_list[0]
            else:
                return
                
            all_keys = pm.keyframe(sel, query=True, timeChange=True)
            
            keyframe_list = list(set(all_keys))
            keyframe_list.sort()            


            
        else:
            time = pm.currentTime(query=True) + (dir*self.time_step_spinbox.get_value())
            pm.currentTime(time, update=True, edit=True ) 
        
    def set_keyframe(self, modifier):
        
        sel_list = pm.ls(sl=True)
        if sel_list:
            sel = sel_list[0]
        else:
            return
            
        if modifier is QtCore.Qt.Key.Key_Shift:
            pm.cutKey(time=pm.currentTime(query=True), cl=True)
            
        else:
            pm.setKeyframe()
                    
               
    def set_transform(self, dir, modifier=None):
    
        #print(modifier)
        
        tool = self.tool_combobox.get_selected_text().lower()
        
        small_amount = self.step_small_spinbox.get_value()
        big_amount = self.step_big_spinbox.get_value()
        
        if modifier is QtCore.Qt.Key_Shift:
            amount = big_amount
            
        else:
            amount = small_amount
            
            
        if dir is -1:
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

    
    def on_ui_click(self, **kargs):

        modifier = None
     
        q_modifier = QtGui.QApplication.keyboardModifiers()
        if q_modifier == QtCore.Qt.ShiftModifier:
            modifier = QtCore.Qt.Key_Shift
            
        if q_modifier == QtCore.Qt.AltModifier:
            modifier = QtCore.Qt.Key_Alt
        
    
        # unpack the kargs, look which callback to use
        callback = kargs.get('callback')
        if callback:
            
            if callback is 'set_transform':
                self.set_transform(dir=kargs.get('dir'), modifier=modifier)
    
            elif callback is 'set_time':
                self.set_time(dir=kargs.get('dir'), modifier=modifier)
                
            elif callback is 'set_keyframe':
                self.set_keyframe(modifier=modifier)

                            
    def keyReleaseEvent(self, event):
        
        key = event.key()            
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

