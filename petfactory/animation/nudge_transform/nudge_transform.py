from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm

class Communicate(QtCore.QObject):
    key_pressed = QtCore.Signal(str)
   
class myDoubleSpinBox(QtGui.QDoubleSpinBox):
    
    def __init__(self, *args):
        super(myDoubleSpinBox, self).__init__(*args)        
        self.c = Communicate()
        
    def event(self, event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_S:
            self.c.key_pressed.emit('s')
            return True
            
        return QtGui.QDoubleSpinBox.event(self, event)

class myQSpinBox(QtGui.QSpinBox):
    
    def __init__(self, *args):
        super(myQSpinBox, self).__init__(*args)        
        self.c = Communicate()
        
    def event(self, event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_S:
            self.c.key_pressed.emit('s')
            return True
            
        return QtGui.QSpinBox.event(self, event)


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(220, 277)
        Form.setMinimumSize(QtCore.QSize(220, 0))
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.x_axis_radiobutton = QtGui.QRadioButton(Form)
        self.x_axis_radiobutton.setChecked(True)
        self.x_axis_radiobutton.setObjectName("x_axis_radiobutton")
        self.horizontalLayout.addWidget(self.x_axis_radiobutton)
        self.y_axis_radiobutton = QtGui.QRadioButton(Form)
        self.y_axis_radiobutton.setObjectName("y_axis_radiobutton")
        self.horizontalLayout.addWidget(self.y_axis_radiobutton)
        self.z_axis_radiobutton = QtGui.QRadioButton(Form)
        self.z_axis_radiobutton.setObjectName("z_axis_radiobutton")
        self.horizontalLayout.addWidget(self.z_axis_radiobutton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setMinimumSize(QtCore.QSize(60, 0))
        self.label_2.setMaximumSize(QtCore.QSize(60, 16777215))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.amount_spinbox = myDoubleSpinBox(Form)
        #self.amount_spinbox = QtGui.QDoubleSpinBox(Form)
        self.amount_spinbox.setMinimumSize(QtCore.QSize(100, 0))
        self.amount_spinbox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.amount_spinbox.setDecimals(6)
        self.amount_spinbox.setMinimum(-1000.0)
        self.amount_spinbox.setMaximum(1000.0)
        self.amount_spinbox.setSingleStep(0.1)
        self.amount_spinbox.setProperty("value", 0.1)
        self.amount_spinbox.setObjectName("amount_spinbox")
        self.horizontalLayout_2.addWidget(self.amount_spinbox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.nudge_neg_btn = QtGui.QPushButton(Form)
        self.nudge_neg_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.nudge_neg_btn.setMaximumSize(QtCore.QSize(100, 100))
        self.nudge_neg_btn.setObjectName("nudge_neg_btn")
        self.horizontalLayout_3.addWidget(self.nudge_neg_btn)
        self.nudge_pos_btn = QtGui.QPushButton(Form)
        self.nudge_pos_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.nudge_pos_btn.setMaximumSize(QtCore.QSize(100, 100))
        self.nudge_pos_btn.setObjectName("nudge_pos_btn")
        self.horizontalLayout_3.addWidget(self.nudge_pos_btn)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setMinimumSize(QtCore.QSize(60, 0))
        self.label_3.setMaximumSize(QtCore.QSize(60, 16777215))
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.time_step_spinbox = myQSpinBox(Form)
        #self.time_step_spinbox = QtGui.QSpinBox(Form)
        self.time_step_spinbox.setMinimumSize(QtCore.QSize(100, 0))
        self.time_step_spinbox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.time_step_spinbox.setProperty("value", 1)
        self.time_step_spinbox.setObjectName("time_step_spinbox")
        self.horizontalLayout_4.addWidget(self.time_step_spinbox)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.timestep_neg_btn = QtGui.QPushButton(Form)
        self.timestep_neg_btn.setObjectName("timestep_neg_btn")
        self.horizontalLayout_5.addWidget(self.timestep_neg_btn)
        self.timestep_pos_btn = QtGui.QPushButton(Form)
        self.timestep_pos_btn.setObjectName("timestep_pos_btn")
        self.horizontalLayout_5.addWidget(self.timestep_pos_btn)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Nudge Transform", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Axis", None, QtGui.QApplication.UnicodeUTF8))
        self.x_axis_radiobutton.setText(QtGui.QApplication.translate("Form", "X", None, QtGui.QApplication.UnicodeUTF8))
        self.y_axis_radiobutton.setText(QtGui.QApplication.translate("Form", "Y", None, QtGui.QApplication.UnicodeUTF8))
        self.z_axis_radiobutton.setText(QtGui.QApplication.translate("Form", "Z", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Amount", None, QtGui.QApplication.UnicodeUTF8))
        self.nudge_neg_btn.setText(QtGui.QApplication.translate("Form", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.nudge_pos_btn.setText(QtGui.QApplication.translate("Form", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Time step", None, QtGui.QApplication.UnicodeUTF8))
        self.timestep_neg_btn.setText(QtGui.QApplication.translate("Form", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.timestep_pos_btn.setText(QtGui.QApplication.translate("Form", ">", None, QtGui.QApplication.UnicodeUTF8))

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
class ControlMainWindow(QtGui.QDialog):

    def __init__(self, parent=None):

        super(ControlMainWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        self.ui.nudge_pos_btn.clicked.connect(self.click_nudge_pos)
        self.ui.nudge_neg_btn.clicked.connect(self.click_nudge_neg)
        
        self.ui.timestep_pos_btn.clicked.connect(self.click_time_pos)
        self.ui.timestep_neg_btn.clicked.connect(self.click_time_neg)
        
        self.ui.amount_spinbox.c.key_pressed.connect(self.key_handler)
        self.ui.time_step_spinbox.c.key_pressed.connect(self.key_handler)
        
    def click_nudge_pos(self):
        self.click_nudge(1)
        
    def click_nudge_neg(self):
        self.click_nudge(-1)
        
    def click_time_pos(self):
        self.change_time(1)
        
    def click_time_neg(self):
        self.change_time(-1)
    
    def click_nudge(self, direction):
        
        if self.ui.x_axis_radiobutton.isChecked():
            self.nudge_it(direction*self.ui.amount_spinbox.value(), 'x')
            
        elif self.ui.y_axis_radiobutton.isChecked():
            self.nudge_it(direction*self.ui.amount_spinbox.value(), 'y')
            
        elif self.ui.z_axis_radiobutton.isChecked():
            self.nudge_it(direction*self.ui.amount_spinbox.value(), 'z')
         
    def nudge_it(self, amount, axis):
        
        sel_list = pm.ls(sl=True)

        if len(sel_list) < 1:
            pm.warning('Nothing is selected!')
            
        else:
            
            if isinstance(sel_list[0], pm.nodetypes.Transform):
                
                if axis is 'x':
                    pm.move(amount, localSpace=True, x=True, r=True)
                    
                if axis is 'y':
                    pm.move(amount, localSpace=True, y=True, r=True)
                    
                if axis is 'z':
                    pm.move(amount, localSpace=True, z=True, r=True)
                
            else:
                pm.warning('Please select a Transform node')

    def change_time(self, direction):
        time = pm.currentTime(query=True) + (direction*self.ui.time_step_spinbox.value())
        pm.currentTime(time, update=True, edit=True ) 
        
    def key_handler(self, key_string):
        if key_string == 's':
            pm.setKeyframe()
                      
def show():
    myWin = ControlMainWindow(parent=maya_main_window())
    myWin.show()
