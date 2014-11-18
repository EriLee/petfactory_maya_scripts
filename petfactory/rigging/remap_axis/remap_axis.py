from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(475, 301)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Form)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QtGui.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.source_node_lineedit = QtGui.QLineEdit(self.groupBox)
        self.source_node_lineedit.setMinimumSize(QtCore.QSize(300, 0))
        self.source_node_lineedit.setObjectName("source_node_lineedit")
        self.horizontalLayout.addWidget(self.source_node_lineedit)
        self.source_node_button = QtGui.QPushButton(self.groupBox)
        self.source_node_button.setObjectName("source_node_button")
        self.horizontalLayout.addWidget(self.source_node_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setMinimumSize(QtCore.QSize(60, 0))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.target_node_lineedit = QtGui.QLineEdit(self.groupBox)
        self.target_node_lineedit.setMinimumSize(QtCore.QSize(300, 0))
        self.target_node_lineedit.setObjectName("target_node_lineedit")
        self.horizontalLayout_2.addWidget(self.target_node_lineedit)
        self.target_node_button = QtGui.QPushButton(self.groupBox)
        self.target_node_button.setObjectName("target_node_button")
        self.horizontalLayout_2.addWidget(self.target_node_button)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(Form)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setMinimumSize(QtCore.QSize(70, 0))
        self.label_3.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.aim_vector_combobox = QtGui.QComboBox(self.groupBox_2)
        self.aim_vector_combobox.setObjectName("aim_vector_combobox")
        self.horizontalLayout_3.addWidget(self.aim_vector_combobox)
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setMinimumSize(QtCore.QSize(70, 0))
        self.label_4.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.aim_axis_combobox = QtGui.QComboBox(self.groupBox_2)
        self.aim_axis_combobox.setObjectName("aim_axis_combobox")
        self.horizontalLayout_3.addWidget(self.aim_axis_combobox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setMinimumSize(QtCore.QSize(70, 0))
        self.label_5.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_4.addWidget(self.label_5)
        self.up_vector_combobox = QtGui.QComboBox(self.groupBox_2)
        self.up_vector_combobox.setObjectName("up_vector_combobox")
        self.horizontalLayout_4.addWidget(self.up_vector_combobox)
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setMinimumSize(QtCore.QSize(70, 0))
        self.label_6.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_4.addWidget(self.label_6)
        self.up_axis_combobox = QtGui.QComboBox(self.groupBox_2)
        self.up_axis_combobox.setObjectName("up_axis_combobox")
        self.horizontalLayout_4.addWidget(self.up_axis_combobox)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem2)
        self.doit_button = QtGui.QPushButton(Form)
        self.doit_button.setMinimumSize(QtCore.QSize(100, 0))
        self.doit_button.setMaximumSize(QtCore.QSize(100, 16777215))
        self.doit_button.setObjectName("doit_button")
        self.horizontalLayout_5.addWidget(self.doit_button)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Remap Axis", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Form", "Nodes", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Source", None, QtGui.QApplication.UnicodeUTF8))
        self.source_node_button.setText(QtGui.QApplication.translate("Form", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Target", None, QtGui.QApplication.UnicodeUTF8))
        self.target_node_button.setText(QtGui.QApplication.translate("Form", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Form", "Axis", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Aim Vector", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Form", "Aim Axis", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Form", "Up Vector", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Form", "Up Axis", None, QtGui.QApplication.UnicodeUTF8))
        self.doit_button.setText(QtGui.QApplication.translate("Form", "Do it!", None, QtGui.QApplication.UnicodeUTF8))



def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
class ControlMainWindow(QtGui.QDialog):
 
    def __init__(self, parent=None):
 
        super(ControlMainWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # set up the comboboxes
        axis_enum = ['x', 'y', 'z']
        self.ui.aim_vector_combobox.addItems(axis_enum)
        self.ui.aim_vector_combobox.setCurrentIndex(0)
        
        self.ui.aim_axis_combobox.addItems(axis_enum)
        self.ui.aim_axis_combobox.setCurrentIndex(1)
                
        self.ui.up_vector_combobox.addItems(axis_enum)
        self.ui.up_vector_combobox.setCurrentIndex(0)
        
        self.ui.up_axis_combobox.addItems(axis_enum)
        self.ui.up_axis_combobox.setCurrentIndex(1)
        
        # setup buttons
        self.ui.doit_button.clicked.connect(self.doit_button_clicked)
        
        self.ui.source_node_button.clicked.connect(self.populate_line_edit)
        self.ui.target_node_button.clicked.connect(self.populate_line_edit)
        
    def doit_button_clicked(self, *args):
        
        source_node_name = self.ui.source_node_lineedit.text()
        target_node_name = self.ui.target_node_lineedit.text()
        
        if len(source_node_name) < 1 or len(target_node_name) < 1:
            pm.warning('Please enter Source and Target nodes!')
            return

        try:
            source_node = pm.PyNode(source_node_name)
        except pm.general.MayaNodeError as e:
            print('{0} is not a valid transform'.format(source_node_name))
            return
            
        try:
            target_node = pm.PyNode(target_node_name)
        except pm.general.MayaNodeError as e:
            print('{0} is not a valid transform'.format(target_node_name))
            return
            
        
        if not isinstance(source_node, pm.nodetypes.Transform):
            pm.warning('Source node is not a transform node')
            return
            
        if not isinstance(target_node, pm.nodetypes.Transform):
            pm.warning('Target node is not a transform node')
            return
            
        tm = source_node.getMatrix()
        target_node.setMatrix(tm)
            
                
    def populate_line_edit(self, *args):
        
        sel = pm.ls(sl=True)
        
        if sel:
        	if isinstance(sel[0], pm.nodetypes.Transform):
        	    node_name = sel[0].longName()
        	else:
        		pm.warning('Transform nodes only!')
        		return
        else:
            return
        

        if self.sender() is self.ui.source_node_button:
            self.ui.source_node_lineedit.setText(node_name) 
            
        if self.sender() is self.ui.target_node_button:
            self.ui.target_node_lineedit.setText(node_name)

        
        
myWin = ControlMainWindow(parent=maya_main_window())
myWin.show()