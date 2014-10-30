from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(226, 199)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(Form)
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
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.amount_spinbox = QtGui.QSpinBox(Form)
        self.amount_spinbox.setMinimumSize(QtCore.QSize(100, 0))
        self.amount_spinbox.setObjectName("amount_spinbox")
        self.horizontalLayout_2.addWidget(self.amount_spinbox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.nudge_pos_btn = QtGui.QPushButton(Form)
        self.nudge_pos_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.nudge_pos_btn.setMaximumSize(QtCore.QSize(100, 100))
        self.nudge_pos_btn.setObjectName("nudge_pos_btn")
        self.horizontalLayout_3.addWidget(self.nudge_pos_btn)
        self.nudge_neg_btn = QtGui.QPushButton(Form)
        self.nudge_neg_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.nudge_neg_btn.setMaximumSize(QtCore.QSize(100, 100))
        self.nudge_neg_btn.setObjectName("nudge_neg_btn")
        self.horizontalLayout_3.addWidget(self.nudge_neg_btn)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Axis", None, QtGui.QApplication.UnicodeUTF8))
        self.x_axis_radiobutton.setText(QtGui.QApplication.translate("Form", "X", None, QtGui.QApplication.UnicodeUTF8))
        self.y_axis_radiobutton.setText(QtGui.QApplication.translate("Form", "Y", None, QtGui.QApplication.UnicodeUTF8))
        self.z_axis_radiobutton.setText(QtGui.QApplication.translate("Form", "Z", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Amount", None, QtGui.QApplication.UnicodeUTF8))
        self.nudge_pos_btn.setText(QtGui.QApplication.translate("Form", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.nudge_neg_btn.setText(QtGui.QApplication.translate("Form", "-", None, QtGui.QApplication.UnicodeUTF8))





def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
class ControlMainWindow(QtGui.QDialog):

    def __init__(self, parent=None):

        super(ControlMainWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
    
def show():
    myWin = ControlMainWindow(parent=maya_main_window())
    myWin.show()
    
show()