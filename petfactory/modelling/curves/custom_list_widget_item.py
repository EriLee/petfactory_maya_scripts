from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
from PySide import QtCore, QtGui

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

'''
class QCustomQWidget (QtGui.QWidget):
    def __init__ (self, parent = None):
        super(QCustomQWidget, self).__init__(parent)
        
        self.textQVBoxLayout = QtGui.QVBoxLayout()
        self.textUpQLabel    = QtGui.QLabel('apa')
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        self.setLayout(self.textQVBoxLayout)
'''     

class QCustomQWidget (QtGui.QWidget):
    def __init__ (self, name, parent=None):
        super(QCustomQWidget, self).__init__(parent)
        
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.setLayout(self.horizontalLayout)
        
        self.title_label = QtGui.QLabel(name)
        self.title_label.setMinimumSize(QtCore.QSize(120, 0))
        self.horizontalLayout.addWidget(self.title_label)
        
        self.inner_radius_spinbox = QtGui.QDoubleSpinBox()
        self.horizontalLayout.addWidget(self.inner_radius_spinbox)
        
        self.outer_radius_spinbox = QtGui.QDoubleSpinBox()
        self.horizontalLayout.addWidget(self.outer_radius_spinbox)

   
# the list widget class    
class Ui_Form(object):
    
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(336, 520)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.list_widget = QtGui.QListWidget(Form)
        self.list_widget.setObjectName("list_widget")
        self.verticalLayout.addWidget(self.list_widget)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        
        for i in range(10):

            item = QtGui.QListWidgetItem(self.list_widget)
            item_widget = QCustomQWidget('Curve {0}'.format(i))
            
            item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)
            
            
        self.build_button = QtGui.QPushButton('Push it!')
        self.verticalLayout.addWidget(self.build_button)
   

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))


# the main ui class  
class ControlMainWindow(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(ControlMainWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
win = ControlMainWindow(parent=maya_main_window())
win.show()