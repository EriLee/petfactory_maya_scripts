from PySide import QtCore, QtGui
from functools import partial

def add_spinbox(label, parent_layout, min=None, max=None, default=None, double_spinbox=False):
    
    horiz_layout = QtGui.QHBoxLayout()
    parent_layout.addLayout(horiz_layout)

    label = QtGui.QLabel(label)
    label.setMinimumWidth(100)
    horiz_layout.addWidget(label)

    horiz_layout.addStretch()

    spinbox = QtGui.QSpinBox() if not double_spinbox else QtGui.QDoubleSpinBox()

    if min:
        spinbox.setMinimum(min)
    if max:
        spinbox.setMaximum(max)
    if default:
        spinbox.setValue(default)


    horiz_layout.addWidget(spinbox)
    spinbox.setMinimumWidth(100)

    return spinbox


def add_populate_lineedit(label, parent_layout, callback=None, kwargs={}):
    
    horiz_layout = QtGui.QHBoxLayout()
    parent_layout.addLayout(horiz_layout)

    button = QtGui.QPushButton(label)
    button.setMinimumWidth(80)
    horiz_layout.addWidget(button)

    lineedit = QtGui.QLineEdit()
    horiz_layout.addWidget(lineedit)
    lineedit.setMinimumWidth(100)

    
    if callback is not None:
        
        kwargs['lineedit'] = lineedit
        button.clicked.connect(partial(callback, **kwargs))

    return lineedit