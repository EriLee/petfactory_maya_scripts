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
        spinbox.setMinimum(max)
    if default:
        spinbox.setValue(default)
        
        
    horiz_layout.addWidget(spinbox)
    spinbox.setMinimumWidth(100)
    
    return spinbox