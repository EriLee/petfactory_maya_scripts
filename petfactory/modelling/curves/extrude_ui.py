def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
# the main ui class  
class Curve_spreadsheet(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(Curve_spreadsheet, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
         
        self.curve = None
        
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        
        self.path_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.path_horiz_layout)

        self.path_label = QtGui.QLabel('Select Profile')
        self.path_horiz_layout.addWidget(self.path_label)
        
        self.path_line_edit = QtGui.QLineEdit()
        self.path_horiz_layout.addWidget(self.path_line_edit)
        
        self.add_path_button = QtGui.QPushButton('   <--   ')
        self.path_horiz_layout.addWidget(self.add_path_button)
        self.add_path_button.clicked.connect(self.add_path_click)
 
        
        self.build_button = QtGui.QPushButton('Extrude')
        self.vertical_layout.addWidget(self.build_button)
        self.build_button.clicked.connect(self.on_build_click)
    
    def add_path_click(self):
         
        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a NurbsCurve transform')
            return
        
        if not isinstance(sel_list[0], pm.nodetypes.Transform):
            pm.warning('Please select a NurbsCurve transform')
            return
        
        try:
            crv = sel_list[0].getShape()
            
        except:
            pm.warning('Please select a NurbsCurve transform')
            return

        
        self.curve = crv     
        crv_name = crv.longName()
            
            
        self.path_line_edit.setText(crv_name)

        
    def on_build_click(self):
        
        sel_list = pm.ls(sl=True)
        
        if self.curve is None:
            pm.warning('No profile curve')
            return
            
        if not sel_list:
            pm.warning('Please select a NurbsCurve transform')
            return
        
        if not isinstance(sel_list[0], pm.nodetypes.Transform):
            pm.warning('Please select a NurbsCurve transform')
            return
        
        try:
            crv = sel_list[0].getShape()
            
        except:
            pm.warning('Please select a NurbsCurve transform')
            return
            
        
        for sel in sel_list:
            pm.extrude(self.curve, sel, extrudeType=2, useComponentPivot=1, fixedPath=True, useProfileNormal=True)
        


       
win = Curve_spreadsheet(parent=maya_main_window())
win.show()
