from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm

try:
    import keyframes

except ImportError as e:
    print('Module keyframes must be imported', e)


from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(452, 342)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Form)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.time_range_GB = QtGui.QGroupBox(Form)
        self.time_range_GB.setMaximumSize(QtCore.QSize(500, 140))
        self.time_range_GB.setObjectName("time_range_GB")
        self.verticalLayout = QtGui.QVBoxLayout(self.time_range_GB)
        self.verticalLayout.setObjectName("verticalLayout")
        self.time_range_HL = QtGui.QHBoxLayout()
        self.time_range_HL.setSpacing(10)
        self.time_range_HL.setObjectName("time_range_HL")
        self.label = QtGui.QLabel(self.time_range_GB)
        self.label.setMinimumSize(QtCore.QSize(100, 0))
        self.label.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.time_range_HL.addWidget(self.label)
        self.use_time_slider_RB = QtGui.QRadioButton(self.time_range_GB)
        self.use_time_slider_RB.setMinimumSize(QtCore.QSize(120, 0))
        self.use_time_slider_RB.setMaximumSize(QtCore.QSize(120, 16777215))
        self.use_time_slider_RB.setChecked(True)
        self.use_time_slider_RB.setObjectName("use_time_slider_RB")
        self.time_range_HL.addWidget(self.use_time_slider_RB)
        self.use_start_end_RB = QtGui.QRadioButton(self.time_range_GB)
        self.use_start_end_RB.setMinimumSize(QtCore.QSize(150, 0))
        self.use_start_end_RB.setMaximumSize(QtCore.QSize(150, 16777215))
        self.use_start_end_RB.setObjectName("use_start_end_RB")
        self.time_range_HL.addWidget(self.use_start_end_RB)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.time_range_HL.addItem(spacerItem)
        self.verticalLayout.addLayout(self.time_range_HL)
        self.start_time_HL = QtGui.QHBoxLayout()
        self.start_time_HL.setSpacing(10)
        self.start_time_HL.setObjectName("start_time_HL")
        self.start_time_L = QtGui.QLabel(self.time_range_GB)
        self.start_time_L.setEnabled(True)
        self.start_time_L.setMinimumSize(QtCore.QSize(100, 0))
        self.start_time_L.setMaximumSize(QtCore.QSize(100, 16777215))
        self.start_time_L.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.start_time_L.setObjectName("start_time_L")
        self.start_time_HL.addWidget(self.start_time_L)
        self.start_time_DSB = QtGui.QDoubleSpinBox(self.time_range_GB)
        self.start_time_DSB.setEnabled(False)
        self.start_time_DSB.setMinimumSize(QtCore.QSize(100, 0))
        self.start_time_DSB.setMaximumSize(QtCore.QSize(100, 16777215))
        self.start_time_DSB.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.start_time_DSB.setDecimals(0)
        self.start_time_DSB.setMinimum(-1000000.0)
        self.start_time_DSB.setMaximum(1000000.0)
        self.start_time_DSB.setObjectName("start_time_DSB")
        self.start_time_HL.addWidget(self.start_time_DSB)
        spacerItem1 = QtGui.QSpacerItem(100, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.start_time_HL.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.start_time_HL)
        self.end_time_HL = QtGui.QHBoxLayout()
        self.end_time_HL.setSpacing(10)
        self.end_time_HL.setObjectName("end_time_HL")
        self.end_time_L = QtGui.QLabel(self.time_range_GB)
        self.end_time_L.setMinimumSize(QtCore.QSize(100, 0))
        self.end_time_L.setMaximumSize(QtCore.QSize(100, 16777215))
        self.end_time_L.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.end_time_L.setObjectName("end_time_L")
        self.end_time_HL.addWidget(self.end_time_L)
        self.end_time_DSB = QtGui.QDoubleSpinBox(self.time_range_GB)
        self.end_time_DSB.setEnabled(False)
        self.end_time_DSB.setMinimumSize(QtCore.QSize(100, 0))
        self.end_time_DSB.setMaximumSize(QtCore.QSize(100, 16777215))
        self.end_time_DSB.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.end_time_DSB.setDecimals(0)
        self.end_time_DSB.setMinimum(-1000000.0)
        self.end_time_DSB.setMaximum(1000000.0)
        self.end_time_DSB.setObjectName("end_time_DSB")
        self.end_time_HL.addWidget(self.end_time_DSB)
        spacerItem2 = QtGui.QSpacerItem(100, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.end_time_HL.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.end_time_HL)
        self.verticalLayout_3.addWidget(self.time_range_GB)
        self.groupBox = QtGui.QGroupBox(Form)
        self.groupBox.setMaximumSize(QtCore.QSize(500, 200))
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.file_format_HL = QtGui.QHBoxLayout()
        self.file_format_HL.setObjectName("file_format_HL")
        self.file_format_L = QtGui.QLabel(self.groupBox)
        self.file_format_L.setEnabled(True)
        self.file_format_L.setMinimumSize(QtCore.QSize(100, 0))
        self.file_format_L.setMaximumSize(QtCore.QSize(100, 16777215))
        self.file_format_L.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.file_format_L.setObjectName("file_format_L")
        self.file_format_HL.addWidget(self.file_format_L)
        self.file_format_CB = QtGui.QComboBox(self.groupBox)
        self.file_format_CB.setMinimumSize(QtCore.QSize(120, 0))
        self.file_format_CB.setMaximumSize(QtCore.QSize(150, 16777215))
        self.file_format_CB.setObjectName("file_format_CB")
        self.file_format_HL.addWidget(self.file_format_CB)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.file_format_HL.addItem(spacerItem3)
        self.verticalLayout_4.addLayout(self.file_format_HL)
        self.scale_HL = QtGui.QHBoxLayout()
        self.scale_HL.setSpacing(10)
        self.scale_HL.setObjectName("scale_HL")
        self.scale_L = QtGui.QLabel(self.groupBox)
        self.scale_L.setMinimumSize(QtCore.QSize(100, 0))
        self.scale_L.setMaximumSize(QtCore.QSize(100, 16777215))
        self.scale_L.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.scale_L.setObjectName("scale_L")
        self.scale_HL.addWidget(self.scale_L)
        self.scale_DSB = QtGui.QDoubleSpinBox(self.groupBox)
        self.scale_DSB.setEnabled(True)
        self.scale_DSB.setMinimumSize(QtCore.QSize(100, 0))
        self.scale_DSB.setMaximumSize(QtCore.QSize(100, 16777215))
        self.scale_DSB.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.scale_DSB.setDecimals(1)
        self.scale_DSB.setMinimum(-10000000.0)
        self.scale_DSB.setMaximum(10000000.0)
        self.scale_DSB.setObjectName("scale_DSB")
        self.scale_HL.addWidget(self.scale_DSB)
        spacerItem4 = QtGui.QSpacerItem(100, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.scale_HL.addItem(spacerItem4)
        self.verticalLayout_4.addLayout(self.scale_HL)
        self.verticalLayout_3.addWidget(self.groupBox)
        spacerItem5 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem5)
        self.frame = QtGui.QFrame(Form)
        self.frame.setMinimumSize(QtCore.QSize(0, 0))
        self.frame.setMaximumSize(QtCore.QSize(500, 50))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.export_HL = QtGui.QHBoxLayout()
        self.export_HL.setObjectName("export_HL")
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.export_HL.addItem(spacerItem6)
        self.export_BTN = QtGui.QPushButton(self.frame)
        self.export_BTN.setObjectName("export_BTN")
        self.export_HL.addWidget(self.export_BTN)
        self.verticalLayout_2.addLayout(self.export_HL)
        self.verticalLayout_3.addWidget(self.frame)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Export keyframe data", None, QtGui.QApplication.UnicodeUTF8))
        self.time_range_GB.setTitle(QtGui.QApplication.translate("Form", "Time range", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Time range:", None, QtGui.QApplication.UnicodeUTF8))
        self.use_time_slider_RB.setText(QtGui.QApplication.translate("Form", "Time Slider", None, QtGui.QApplication.UnicodeUTF8))
        self.use_start_end_RB.setText(QtGui.QApplication.translate("Form", "Start / End", None, QtGui.QApplication.UnicodeUTF8))
        self.start_time_L.setText(QtGui.QApplication.translate("Form", "Start time:", None, QtGui.QApplication.UnicodeUTF8))
        self.end_time_L.setText(QtGui.QApplication.translate("Form", "End time:", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Form", "Export options", None, QtGui.QApplication.UnicodeUTF8))
        self.file_format_L.setText(QtGui.QApplication.translate("Form", "File format:", None, QtGui.QApplication.UnicodeUTF8))
        self.scale_L.setText(QtGui.QApplication.translate("Form", "Scale", None, QtGui.QApplication.UnicodeUTF8))
        self.export_BTN.setText(QtGui.QApplication.translate("Form", "Export", None, QtGui.QApplication.UnicodeUTF8))

# end Qt designer

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    

class ControlMainWindow(QtGui.QDialog):

    def __init__(self, parent=None):

        super(ControlMainWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        self.use_time_slider = True
        
        self.ui.use_time_slider_RB.clicked.connect(self.click_radiobutton)
        self.ui.use_start_end_RB.clicked.connect(self.click_radiobutton)
        self.ui.export_BTN.clicked.connect(self.click_export)
        
        file_formats = ['Maya / AE (.ma)', 'Nuke (.nk)', 'Nuke (copy to clipboard)', 'Data (.json)']
        self.ui.file_format_CB.addItems(file_formats)

        self.ui.scale_DSB.setValue(1.0)
        

    def click_radiobutton(self):
        
        if self.sender() is self.ui.use_time_slider_RB:
            self.use_time_slider = True
            self.ui.start_time_DSB.setEnabled(False)
            self.ui.end_time_DSB.setEnabled(False)
            
        elif self.sender() is self.ui.use_start_end_RB:
            self.use_time_slider = False
            self.ui.start_time_DSB.setEnabled(True)
            self.ui.end_time_DSB.setEnabled(True)

    def click_export(self):
        
        sel = pm.ls(sl=True)

        if len(sel) < 1:
            pm.warning('Select transform(s) and camera(s)')
            return

        if self.use_time_slider:
            start_time = pm.playbackOptions(q=True, minTime=True) 
            end_time = pm.playbackOptions(q=True, maxTime=True) 
            
        else:
            start_time = self.ui.start_time_DSB.value()
            end_time = self.ui.end_time_DSB.value()
        
        file_format_index = self.ui.file_format_CB.currentIndex()
        
        if file_format_index is 0:
            file_format = 'ma'
        elif file_format_index is 1:
            file_format = 'nk'
        elif file_format_index is 2:
            file_format = 'nk_copy'
        elif file_format_index is 3:
            file_format = 'json'

        scale = self.ui.scale_DSB.value()

        if scale == 1.0:
        	scale = None

        keyframes.write_data(sel, int(round(start_time)), int(round(end_time)), file_format, scale)
        

def show():
    myWin = ControlMainWindow(parent=maya_main_window())
    myWin.show()