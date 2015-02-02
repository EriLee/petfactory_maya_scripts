from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm



def build_ribbon(width, depth, num_u_patches=10):
    
    plane_u_patches = num_u_patches - 1
    plane_length_ratio = float(depth) / width
    plane_pivot_pos = width*.5, 0, 0
    
    ribbon_plane = pm.nurbsPlane(ax=(0,1,0), n='ribbon_geo', ch=False, patchesU=plane_u_patches, width=width, lengthRatio=plane_length_ratio, pivot=plane_pivot_pos)

    return ribbon_plane[0]
    
    
def add_follicles(nurbs_surface, num_follicles=10, direction='u', name='ribbon'):
    
    # chack that the user has provided:
    # a NurbsSurface
    # that the direction is valid 'u' or 'v'
    
    
    # max u, min u, max v, min v
    min_u, max_u, min_v, max_v = nurbs_surface.getKnotDomain()

    if direction == 'u':
        uv_inc = max_u / (num_follicles-1)
        
    if direction == 'v':
        uv_inc = max_v / (num_follicles-1)
  
    follicle_grp = pm.group(em=True, n='{0}_follicle_grp'.format(name))
    
    ret_dict = {}
    follicle_shape_list = []
    follicle_transform_list = []
    
    ret_dict['follicle_grp'] = follicle_grp
    ret_dict['follicle_shape_list'] = follicle_shape_list
    ret_dict['follicle_transform_list'] = follicle_transform_list
        
    
    for n in range(num_follicles):
    
        follicle_shape = pm.createNode('follicle', ss=1, n='{0}_FollicleShape_{1}'.format(name, n))
        follicle_transform = follicle_shape.getParent()
        
        follicle_shape_list.append(follicle_shape)
        follicle_transform_list.append(follicle_transform)
        
        follicle_shape.outRotate >> follicle_transform.rotate
        follicle_shape.outTranslate >> follicle_transform.translate
        
        nurbs_surface.local >> follicle_shape.inputSurface
        nurbs_surface.worldMatrix[0] >> follicle_shape.inputWorldMatrix

        if direction == 'u':
            follicle_shape.parameterU.set(n * uv_inc)
            follicle_shape.parameterV.set(.5)
            
        if direction == 'v':
            follicle_shape.parameterU.set(.5)
            follicle_shape.parameterV.set(n * uv_inc)
            
        pm.parent(follicle_transform, follicle_grp)
    
    return ret_dict
            

def add_follicle_joints(follicle_transform_list):

    for index, follicle_transform in enumerate(follicle_transform_list):
        jnt = pm.createNode('joint', ss=True, n='follicle_jnt_{0}'.format(index))
        pm.parent(jnt, follicle_transform)
        jnt.translate.set(0,0,0)
    


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    

# the main ui class  
class CreateRibbonUI(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(CreateRibbonUI, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300, 350)
        self.setWindowTitle("Create Ribbon")
                
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        self.width_spinbox = CreateRibbonUI.add_spinbox(label='Ribbon Width', min=.1, layout=self.vertical_layout, default=35, double_spinbox=True)
        self.depth_spinbox = CreateRibbonUI.add_spinbox(label='Ribbon Depth', min=.1, layout=self.vertical_layout, default=1, double_spinbox=True)
        self.num_u_patches_spinbox = CreateRibbonUI.add_spinbox(label='Number of U Patches', min=1, layout=self.vertical_layout, default=10)
        self.num_follicles_spinbox = CreateRibbonUI.add_spinbox(label='Number of follicles', min=.1, layout=self.vertical_layout, default=50)
        
        
        self.vertical_layout.addStretch()
        
        self.create_button = QtGui.QPushButton('Build Ribbon')
        self.vertical_layout .addWidget(self.create_button)
        self.create_button.clicked.connect(self.build_button_clicked)
        

    @staticmethod
    def add_spinbox(label, layout, min=None, max=None, default=None, double_spinbox=False):
        
        horiz_layout = QtGui.QHBoxLayout()
        layout.addLayout(horiz_layout)

        label = QtGui.QLabel(label)
        label.setMinimumWidth(100)
        horiz_layout.addWidget(label)
        
        horiz_layout.addStretch()
         
        spinbox = QtGui.QSpinBox() if not double_spinbox else QtGui.QDoubleSpinBox()
        if min:
            spinbox.setMinimum(min)
        if max:
            spinbox.setMaximun(max)
        if default:
            spinbox.setValue(default)
            
        horiz_layout.addWidget(spinbox)
        spinbox.setMinimumWidth(100)
        
        return spinbox
        
    def build_button_clicked(self):
        
        width = self.width_spinbox.value()
        depth = self.depth_spinbox.value()
        num_u_patches = self.num_u_patches_spinbox.value()
        num_follicles= self.num_follicles_spinbox.value()
        
        #print(width, num_u_patches, num_joints)
        
            
        # build the ribbon surface
        ribbon = build_ribbon(width=width, depth=depth, num_u_patches=num_u_patches)
        
        # add follicles
        follicle_dict = add_follicles(nurbs_surface=ribbon, num_follicles=num_follicles)
        
        # add joint to the follicles
        add_follicle_joints(follicle_dict.get('follicle_transform_list'))
        
        

def show():      
    win = CreateRibbonUI(parent=maya_main_window())
    win.show()


#show()