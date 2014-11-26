# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/johan/Dev/maya/petfactory_maya_scripts/petfactory/modelling/curves/radius_slider_widget_designer.ui'
#
# Created: Wed Nov 26 00:01:48 2014
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(438, 54)
        self.layoutWidget = QtGui.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 10, 391, 26))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.title_label = QtGui.QLabel(self.layoutWidget)
        self.title_label.setMinimumSize(QtCore.QSize(120, 0))
        self.title_label.setObjectName("title_label")
        self.horizontalLayout.addWidget(self.title_label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setMinimumSize(QtCore.QSize(30, 0))
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.inner_radius_spinbox = QtGui.QDoubleSpinBox(self.layoutWidget)
        self.inner_radius_spinbox.setMaximum(999.0)
        self.inner_radius_spinbox.setObjectName("inner_radius_spinbox")
        self.horizontalLayout.addWidget(self.inner_radius_spinbox)
        self.label_2 = QtGui.QLabel(self.layoutWidget)
        self.label_2.setMinimumSize(QtCore.QSize(30, 0))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.outer_radius_spinbox = QtGui.QDoubleSpinBox(self.layoutWidget)
        self.outer_radius_spinbox.setMaximum(999.0)
        self.outer_radius_spinbox.setObjectName("outer_radius_spinbox")
        self.horizontalLayout.addWidget(self.outer_radius_spinbox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.title_label.setText(QtGui.QApplication.translate("Form", "Radius", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Inner", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Outer", None, QtGui.QApplication.UnicodeUTF8))

