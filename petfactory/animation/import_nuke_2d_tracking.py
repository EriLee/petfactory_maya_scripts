import pymel.core as pm
import math
import json
import pprint


def plot_imageplane_corners(depth, theta, ratio):

    half_width = math.tan(theta/2) * depth
    half_height = half_width/ratio

    dot(pos=((half_width, half_height, -depth)), name='tr')
    dot(pos=((-half_width, half_height, -depth)), name='tl')
    dot(pos=((-half_width, -half_height, -depth)), name='bl')
    dot(pos=((half_width, -half_height, -depth)), name='br')
    
    
def plot_pos_on_imageplane(depth, theta, width, height, x, y):
    
    ratio = float(width)/height
    
    half_width = math.tan(theta/2) * depth
    half_height = half_width/ratio
    
    bottom_left_x = -half_width
    bottom_left_y = -half_height
    
    full_width = half_width * 2
    full_height = half_height * 2
    
    x_percent = x / width
    y_percent = y / height
    
    x_offset = full_width * x_percent
    y_offset = full_height * y_percent
      
    return (bottom_left_x+x_offset, bottom_left_y+y_offset, -depth)

    
def dot(pos, name):
    sp = pm.polySphere(name=name, r=5)[0]
    sp.translate.set(pos)


def import_data(file_path, camera, depth, width, height):
    
    camera_shape = camera.getShape()
    hfov_deg = camera_shape.getHorizontalFieldOfView()
    
    theta = pm.util.radians(hfov_deg)

    # read the json
    data = None
    with open(file_path, 'r') as f:
        data = f.read()
    
    json_data = json.loads(data)
    
    # get the camera transfomration matrix
    tm = pm.datatypes.TransformationMatrix(camera.getMatrix())
    cam_pos = tm.getTranslation(space='world')
 
    # get info from the dict
    key = json_data.keys()[0]
    node_dict = json_data.get(key)
    info_dict = node_dict.get('info')
    center_pos = info_dict.get('center_pos')
    first_frame = info_dict.get('first_frame')
    keyframe_list = node_dict.get('keyframes')
    
    # check if the auto keyframe is on
    auto_keyframe_is_on = pm.autoKeyframe(q=True, state=True)
    
    # if auto keyframe is on turn it off
    if auto_keyframe_is_on:
        pm.autoKeyframe(state=False)
         
    loc = pm.spaceLocator()
    loc.setMatrix(tm)
    pm.toggle(loc, localAxis=True)
        
    for index, pos in enumerate(keyframe_list):
        
        pos = plot_pos_on_imageplane(depth=depth, theta=theta, width=width, height=height, x=pos[0]+center_pos[0], y=pos[1]+center_pos[1])
        pm_pos = pm.datatypes.Vector(pos)
        
        pos_tm = pm_pos.rotateBy(tm) + cam_pos
        loc.translate.set(pos_tm[0], pos_tm[1],pos_tm[2])
        
        pm.setKeyframe(loc, attribute='translate', t=first_frame+index)
    
    # turn the auto keyframe back on
    if auto_keyframe_is_on:
        pm.autoKeyframe(state=True)
        



from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
class Import_nuke_2d_track_ui(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(Import_nuke_2d_track_ui, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        

        # layout
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        # add camera 
        self.cam_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.cam_horiz_layout)
        
        self.cam_line_edit = QtGui.QLineEdit()
        self.cam_horiz_layout.addWidget(self.cam_line_edit)
        
        self.add_cam_button = QtGui.QPushButton('Select Camera')
        self.cam_horiz_layout.addWidget(self.add_cam_button)
        self.add_cam_button.clicked.connect(self.add_cam_click)
        
        # depth
        self.depth_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.depth_horiz_layout)
        
        self.depth_label = QtGui.QLabel('Depth')
        self.depth_horiz_layout.addWidget(self.depth_label)
        
        self.depth_spinbox = QtGui.QDoubleSpinBox()
        self.depth_spinbox.setMaximum(9999999)
        self.depth_spinbox.setDecimals(3)
        self.depth_horiz_layout.addWidget(self.depth_spinbox)
        
        # resolution      
        self.resolution_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.resolution_horiz_layout)
        
        combo_label = QtGui.QLabel('Resolution')
        self.resolution_horiz_layout.addWidget(combo_label)
        
        self.resolution_combobox = QtGui.QComboBox(self)
        self.resolution_horiz_layout.addWidget(self.resolution_combobox)
        
        self.resolution_list = [(1280, 720), (1920, 1080)]
        res_string_list = ['{0} x {1}'.format(res[0], res[1]) for res in self.resolution_list]
        self.resolution_combobox.addItems(res_string_list)
        
        # Import
        self.import_button = QtGui.QPushButton('Import 2d Data')
        self.vertical_layout.addWidget(self.import_button)
        self.import_button.clicked.connect(self.import_data)
        

    def add_cam_click(self):
        
        sel_list = pm.ls(sl=True)
        
        if sel_list < 1:
            pm.warning('Please select a camera!')
            return
        
        if not isinstance(sel_list[0], pm.nodetypes.Transform):
            pm.warning('Please select a camera!')
            return
            

        shape = sel_list[0].getShape()
        if not isinstance(shape, pm.nodetypes.Camera):
                pm.warning('Please select a camera!')
                return
                
        self.cam_line_edit.setText(sel_list[0].longName())
            
            
        
    def import_data(self):
        
        resolution = self.resolution_list[self.resolution_combobox.currentIndex()]
        depth = self.depth_spinbox.value()
        camera = self.cam_line_edit.text()
        #print(resolution, depth, camera)
  
        # try to convert to a pymel camera node
        try:
            cam = pm.PyNode(camera)
            
        except pm.general.MayaNodeError as e:
            pm.warning('Object specified is not a valid Camera!')
            return
            
        
        # open the json file
        file_name, selected_filter = QtGui.QFileDialog.getOpenFileName(None, 'Import Keyframes', None, 'JSON (*.json)')
        

        if file_name:
            import_data(file_path=file_name, camera=cam, depth=depth, width=resolution[0], height=resolution[1])

    

def show():      
    win = Import_nuke_2d_track_ui(parent=maya_main_window())
    win.show()
