from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import pymel.core as pm
import pprint
import math

import petfactory.modelling.mesh.extrude_profile as pet_extrude
reload(pet_extrude)

#pm.system.openFile('/Users/johan/Documents/Projects/python_dev/scenes/empty_scene.mb', f=True)

def loc(p, size=.2):
    loc = pm.spaceLocator()
    loc.localScale.set((size,size,size))
    loc.translate.set(p)

def dot(p, r=.2, name='mySphere'):
    sp = pm.polySphere(r=r, n=name)[0]
    sp.translate.set(p)
    pm.toggle(sp, localAxis=True)

   
def worldspace_radius(cv_list, radius, num_points):
    
    vec_aim = pm.datatypes.Vector(cv_list[0] - cv_list[1]).normal()
    vec_up = pm.datatypes.Vector(cv_list[2] - cv_list[1]).normal()
    pos = pm.datatypes.Vector(cv_list[1])
    
    # construct a orthogonalized coordinate space
    vec_cross = vec_aim.cross(vec_up).normal()
    vec_up_ortho = vec_cross.cross(vec_aim).normal()
    
    # create a transformation matrix
    world_tm = pm.datatypes.TransformationMatrix( [   [vec_aim.x, vec_aim.y, vec_aim.z, 0],
                                                      [vec_up_ortho.x, vec_up_ortho.y, vec_up_ortho.z, 0],   
                                                      [vec_cross.x, vec_cross.y, vec_cross.z, 0],   
                                                      [pos.x, pos.y, pos.z, 1] 
                                                        
                                                    ])
                                                    
    # bring the 3d pos to 2d uv space, by using the dot product to project on the orthogonal "base vectors"
    #aim_u = vec_aim.dot(vec_aim)
    #aim_v = vec_aim.dot(vec_up_ortho)
    
    up_u = vec_up.dot(vec_aim)
    up_v = vec_up.dot(vec_up_ortho)
    
    # using atan2 we can find the angle between the aim vec and the up vector.
    # we have used the dot product to "project" the aim vec so that it is projected
    # on the x axis (the adjacent side in the right angled triangle)
    # we want to get the angle from the adjacent side to the mid vector (mid between the aim and up)
    # that is the reason that multiply it with .5.
    theta = math.atan2(up_v, up_u) * .5
    #radius = 2
    #num_points = 12
    
    # The total angle in a triangle is 180 degrees
    # since one angle is 90 deg (pi/2) and the theta ang is known, we can
    # get the remaining angle with 180 - 90 - theta, which can be simplified to
    # 90 - theta i.e. (math.pi/2) - theta, then we multiply by 2 to get the full circle
    # so we do not need to relect the vectors across the mid vec to get the full radius circ
    ang_full = ((math.pi/2) - theta) * 2
    
    # get the adjacent given the opposite (radius) and the angle theta
    # math.tan(theta) = o/a
    # a * math.tan(theta) = o
    # a = a / math.tan(theta)
    adjacent = radius / math.tan(theta)
        
    radius_center = pm.datatypes.Vector(adjacent, radius, 0)
    
    # calculate the positions on the circle
    ang_inc = ang_full/(num_points-1)
    
    # the ang from pos x axis to opposite (negative y axis)
    ang_to_opp = (1.5 * math.pi)
    
    t_matrix_list = []
    for i in range(num_points):
        
        a = ang_to_opp - (ang_inc * i)
        x = math.cos(a) * radius + adjacent
        y = math.sin(a) * radius + radius
        p = pm.datatypes.Vector(x, y, 0)
        
        # create the etransformation matrix
        aim = (radius_center - p).normal()
        up = pm.datatypes.Vector(0,0,1)
        cross = aim.cross(up)
        
  
        tm = pm.datatypes.TransformationMatrix( [   [cross.x, cross.y, cross.z, 0],
                                                    [aim.x, aim.y, aim.z, 0],
                                                    [up.x, up.y, up.z, 0],
                                                    [p.x, p.y, p.z, 1] ])
        
        t_matrix_list.append(tm * world_tm)
        
    return t_matrix_list



def create_profile_points(radius, num_points):
    '''Returns a list of positions (pm.datatypes.Vector) on a circle 
    around the origin, in the xz plane, i.e. y axis as normal'''
    
    ang_inc = (math.pi*2)/num_points
    
    p_list = []
    
    for i in range(num_points):
        u = math.cos(ang_inc*i)*radius
        v = math.sin(ang_inc*i)*radius
        p_list.append(pm.datatypes.Vector(0, v, u))
     
    return p_list
    

def add_division_to_straight_pipe(start_matrix, end_matrix, num_divisions):
    
    ret_matrix_list = []
    
    start_pos = start_matrix.getTranslation(space='world')
    end_pos = end_matrix.getTranslation(space='world')
    
    vec = end_pos - start_pos
    inc = 1.0/(num_divisions-1)
    
    for i in range(num_divisions):
        
        temp_m = pm.datatypes.TransformationMatrix(start_matrix.asRotateMatrix())
        pos = start_pos+vec*i*inc
        temp_m.a30 = pos.x
        temp_m.a31 = pos.y
        temp_m.a32 = pos.z
        ret_matrix_list.append(temp_m)

    return ret_matrix_list
           
# build a transformation matrix list for the start point, all the radius positions and the last point
def create_round_corner_matrix_list(cv_list, num_radius_div):

    num_cv = len(cv_list)
    result_matrix_list = []
    last_matrix = None
    
    # all the radius calculations is done when the index is in range 0 - (length-2)
    # I am using the index in the cv positions array [n:n+3] i.e. if the starting 
    # index is 0 I take aslice of the list starting at 0 index up to 3 (but not including)
    # so index 0,1,2 is used to calculate the radie. so we would get and index error if
    # we go past num_cv-2.
    for index in range(num_cv-2):
        
        # calculate the radius
        tm_list = worldspace_radius(cv_list=cv_list[index:index+3], radius=1, num_points=num_radius_div)
        
        # first cv
        if index is 0:
            
            # get the rotation matrix from the first matrix in the tm_list (the first matrix of the radius)
            # set the translation to the world pos of the first cv
            temp_m = pm.datatypes.TransformationMatrix(tm_list[0].asRotateMatrix())
            temp_m.a30 = cv_list[0].x
            temp_m.a31 = cv_list[0].y
            temp_m.a32 = cv_list[0].z
            
            # add the to matrices of the first straight pipe, then add the radius matrix list
            result_matrix_list.append(add_division_to_straight_pipe(temp_m, tm_list[0], 10))
            result_matrix_list.append(tm_list)
            
            last_matrix = tm_list[-1]

          
        # mid cvs
        else:

            # get the rotation matrix from the last matrix (prevoius radius)
            # set the translation to the world pos of the the first matrix in the current radius matrix list         
            temp_m = pm.datatypes.TransformationMatrix(last_matrix.asRotateMatrix())
            pos = tm_list[0].getTranslation(space='world')
            temp_m.a30 = pos.x
            temp_m.a31 = pos.y
            temp_m.a32 = pos.z
            
            # add the radius list, then the following straight pipe
            result_matrix_list.append(add_division_to_straight_pipe(last_matrix, temp_m, 10))
            result_matrix_list.append(tm_list)
            
            last_matrix = tm_list[-1]
            
 
    # the last cv of the crv, get the ending position of the last straight pipe
    temp_m = pm.datatypes.TransformationMatrix(tm_list[-1].asRotateMatrix())
    temp_m.a30 = cv_list[-1].x
    temp_m.a31 = cv_list[-1].y
    temp_m.a32 = cv_list[-1].z
                
    result_matrix_list.append(add_division_to_straight_pipe(tm_list[-1], temp_m, 10))


    return result_matrix_list
        


def transform_profile_list(result_matrix_list, profile_pos): 
   
    result_pos_list = []
    
    for matrix_list in result_matrix_list:
        
        temp_list = []
        for matrix in matrix_list:
            temp_list.append([pos.rotateBy(matrix) + matrix.getTranslation(space='world') for pos in profile_pos])
            
        result_pos_list.append(temp_list)
            
    return result_pos_list
           

def build_mesh(pos_list):
    
    mesh_list = []
    for p in pos_list:
        mesh_list.append(pet_extrude.mesh_from_pos_list(pos_list=p, name='test'))
    return mesh_list


def add_pipe_fitting(result_matrix_list, mesh=None):
    
    if not isinstance(mesh, pm.nodetypes.Transform):
        pm.warning('fitting mesh not a vaild Transform, will use default')
        mesh = None

    mesh_list = []
    for index, matrix_list in enumerate(result_matrix_list):
        
        # just get the matrix list on even index, i.e. the straight pipes
        if not index%2:

            if mesh:
                mesh_1 = pm.duplicate(mesh)[0]
                mesh_2 = pm.duplicate(mesh)[0]
            else:
                mesh_1 = pm.polyCylinder(r=.50, h=.3, axis=(1,0,0))[0]
                mesh_2 = pm.duplicate(mesh_1)[0]
                
                
            mesh_1.setMatrix(matrix_list[0])
            #pm.toggle(mesh_1, localAxis=True)
            
            # flip the rotation of the second pipe fitting
            tm = matrix_list[-1]
            tm.addRotation((0,0,math.pi), order=1, space='preTransform')
            
            mesh_2.setMatrix(tm)
            #pm.toggle(mesh_2, localAxis=True)
            mesh_list.extend([mesh_1, mesh_2])
            
    return mesh_list
            
'''
#crv = pm.curve(d=1, p=[(10,2,3), (7, 3, 0), (10, 5, -3), (8,10,3), (5,5,0), (0,5,-3)])
#crv = pm.curve(d=1, p=[(10, -5, 0), (0,0,0), (10, 5, 0)])
crv = pm.curve(d=1, p=[(10, -5, 0), (0,0,0), (10, 5, 0), (10,10,0), (0,10,0)])

#crv = pm.ls(sl=True)[0]
cv_list = crv.getCVs(space='world')

# get the matrix list
result_matrix_list = create_round_corner_matrix_list(cv_list, num_radius_div=10)

# create the profile 
profile_pos = create_profile_points(radius=.4, num_points=12)

# get the positions
pos_list = transform_profile_list(result_matrix_list=result_matrix_list, profile_pos=profile_pos)

# build mesh 
mesh_mobj_list = build_mesh(pos_list)
pm_mesh_list = [ pm.PyNode('|{0}'.format(m.name())) for m in mesh_mobj_list]
pipe_grp = pm.group(em=True, name='pipe_grp')
pm.parent(pm_mesh_list, pipe_grp)

# add pipe fitting
dup_mesh=None
try:
    dup_mesh = pm.PyNode('fitting_grp')
except pm.MayaNodeError:
    pm.warning('could not find fitting mesh')

fitting_list = add_pipe_fitting(result_matrix_list, mesh=dup_mesh)
fitting_grp = pm.group(em=True, name='fitting_grp')
pm.parent(fitting_list, fitting_grp)

# create the main group
main_pipe_grp = pm.group(em=True, name='main_pipe_grp')
pm.parent(pipe_grp, fitting_grp, main_pipe_grp)

pm.sets('initialShadingGroup', forceElement=pm_mesh_list)
'''


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
# the main ui class  
class Curve_spreadsheet(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(Curve_spreadsheet, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300, 350)
        self.setWindowTitle("Pipe Tool")
                
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        

        # add path
        self.path_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.path_horiz_layout)
              
        self.add_path_button = QtGui.QPushButton('Add Path')
        self.add_path_button.setMinimumWidth(75)
        self.path_horiz_layout.addWidget(self.add_path_button)
        self.add_path_button.clicked.connect(self.add_path_click)
        
        self.path_line_edit = QtGui.QLineEdit()
        self.path_horiz_layout.addWidget(self.path_line_edit)
        
        # add mesh
        self.fitting_mesh_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.fitting_mesh_horiz_layout)
               
        self.add_fitting_mesh_button = QtGui.QPushButton('Add Mesh')
        self.add_fitting_mesh_button.setMinimumWidth(75)
        self.fitting_mesh_horiz_layout.addWidget(self.add_fitting_mesh_button)
        self.add_fitting_mesh_button.clicked.connect(self.add_fitting_mesh_click)
        
        self.fitting_mesh_line_edit = QtGui.QLineEdit()
        self.fitting_mesh_horiz_layout.addWidget(self.fitting_mesh_line_edit)
        
        
        # table view  
        self.table_view = QtGui.QTableView()
        self.vertical_layout.addWidget(self.table_view)
        
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Radius'])
  
        self.table_view.setModel(self.model)
        
        #v_header = self.table_view.verticalHeader()
        h_header = self.table_view.horizontalHeader()
        h_header.setResizeMode(QtGui.QHeaderView.Stretch)
           
        self.axis_div_spinbox = Curve_spreadsheet.add_int_spinbox('Axis Divisions', self.vertical_layout)
        self.length_div_spinbox = Curve_spreadsheet.add_int_spinbox('Length Divisions', self.vertical_layout)
        self.radial_div_spinbox = Curve_spreadsheet.add_int_spinbox('Radial Divisions', self.vertical_layout)
                
        # build button
        self.build_button_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(self.build_button_horiz_layout)
        
        self.build_button_horiz_layout.addStretch()
        self.build_button = QtGui.QPushButton('Build it!')
        self.build_button.setMinimumWidth(100)
        self.build_button_horiz_layout.addWidget(self.build_button)
        self.build_button.clicked.connect(self.on_build_click)
    
    
    @staticmethod
    def add_int_spinbox(label, parent_layout):
        
        horiz_layout = QtGui.QHBoxLayout()
        parent_layout.addLayout(horiz_layout)

        label = QtGui.QLabel(label)
        label.setMinimumWidth(100)
        horiz_layout.addWidget(label)
        
        horiz_layout.addStretch()
         
        spinbox = QtGui.QSpinBox()
        horiz_layout.addWidget(spinbox)
        spinbox.setMinimumWidth(100)
        
        return spinbox

        
    def add_fitting_mesh_click(self):
        
        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a Mesh transform')
            return
        
        if not isinstance(sel_list[0], pm.nodetypes.Transform):
            pm.warning('Please select a Mesh transform')
            return
        
        try:
            mesh_shape = sel_list[0].getShape()

            if isinstance(mesh_shape, pm.nodetypes.Mesh):
                mesh_name = sel_list[0].longName() 
                
            else:
                pm.warning('Please select a Mesh transform')
                return
            
            
        except pm.general.MayaNodeError as e:
            pm.warning('Please select a Mesh transform', e)
            return
            
        self.fitting_mesh_line_edit.setText(mesh_name)
        
   
    
    def add_path_click(self):
        
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Radius'])
        
        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a NurbsCurve transform')
            return
        
        if not isinstance(sel_list[0], pm.nodetypes.Transform):
            pm.warning('Please select a NurbsCurve transform')
            return
        
        try:
            crv_shape = sel_list[0].getShape()
            
            if isinstance(crv_shape, pm.nodetypes.NurbsCurve):
                crv = sel_list[0]
                
            else:
                pm.warning('Please select a NurbsCurve transform')
                return
            
            
        except pm.general.MayaNodeError as e:
            pm.warning('Please select a NurbsCurve transform', e)
            return
  
        crv_name = crv.longName()    
        self.path_line_edit.setText(crv_name)
        
        cv_list = crv.getCVs(space='world')
        num_cvs = len(cv_list)
        num_corners = num_cvs -2
        
        if num_corners < 1:
            pm.warning('Please select a degree1 curve with more than 2 CVs')
            
        
        for row in range(num_corners):
            
            item_inner = QtGui.QStandardItem('1')

            self.model.setItem(row, 0, item_inner);
    
        
    def on_build_click(self):
        
        radius_list = []
        
        num_rows = self.model.rowCount()
        
        axis_divisions = self.axis_div_spinbox.value()
        length_divisions = self.length_div_spinbox.value()
        radial_divisions = self.radial_div_spinbox.value()
        
        crv_name = self.path_line_edit.text()
        fitting_mesh_name = self.fitting_mesh_line_edit.text()
        
        
        
        for row in range(num_rows):
            
            radius_text = self.model.item(row,0).text()
            
            try:
                radius = float(radius_text)
                
            except ValueError as e:
                pm.warning('The Inner Radius of row {0} is not a valid number'.format(row+1))
                #print(e)
                return None
                
            
            radius_list.append(radius)
        
        print(radius_list, axis_divisions, length_divisions, radial_divisions, fitting_mesh_name, crv_name)
        
        crv = pm.PyNode(crv_name)
        
        cv_list = crv.getCVs(space='world')
        
        # get the matrix list
        result_matrix_list = create_round_corner_matrix_list(cv_list, num_radius_div=radial_divisions)
        
        # create the profile 
        profile_pos = create_profile_points(radius=radius_list[0], num_points=axis_divisions)
        
        # get the positions
        pos_list = transform_profile_list(result_matrix_list=result_matrix_list, profile_pos=profile_pos)
        
        # build mesh 
        mesh_mobj_list = build_mesh(pos_list)
        pm_mesh_list = [ pm.PyNode('|{0}'.format(m.name())) for m in mesh_mobj_list]
        pipe_grp = pm.group(em=True, name='pipe_grp')
        pm.parent(pm_mesh_list, pipe_grp)
        
        # add pipe fitting
        dup_mesh=None
        try:
            dup_mesh = pm.PyNode(fitting_mesh_name)
        except pm.MayaNodeError:
            pm.warning('could not find fitting mesh')
        
        fitting_list = add_pipe_fitting(result_matrix_list, mesh=dup_mesh)
        fitting_grp = pm.group(em=True, name='fitting_grp')
        pm.parent(fitting_list, fitting_grp)
        
        # create the main group
        main_pipe_grp = pm.group(em=True, name='main_pipe_grp')
        pm.parent(pipe_grp, fitting_grp, main_pipe_grp)
        
        pm.sets('initialShadingGroup', forceElement=pm_mesh_list)
                        




def show():      
    win = Curve_spreadsheet(parent=maya_main_window())
    win.show()

try:
    win.close()
except NameError as e:
    print(e)
    
win = Curve_spreadsheet(parent=maya_main_window())
win.move(100, 210)
win.show()






