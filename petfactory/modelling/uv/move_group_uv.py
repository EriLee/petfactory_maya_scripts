from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
import pprint

import math

import pymel.core as pm
import math

def tile_uvs(grp_list, padding):

    first_grp = grp_list[0]
    first_grp_uvs = pm.polyListComponentConversion(first_grp, tuv=True)
    
    (u_min, u_max), (v_min, v_max) = pm.polyEvaluate(first_grp_uvs, boundingBox2d=True)
    
    uv_width = u_max - u_min
    uv_height = v_max - v_min
    
    # calculate how manu time the uv + padding fits within a uv patch
    #max_u_tiles = math.floor(1.0 / (uv_width + (2*padding)))
    #max_v_tiles = math.floor(1.0 / (uv_height + (2*padding)))
    
    # we could calculate how many times the fit within a patch
    # and give a warning if it is the padding that makes the uv patch not fit
    max_u_tiles = math.floor(1.0 / uv_width)
    max_v_tiles = math.floor(1.0 / uv_height)
    
    # calculate the resulting width and height (with padding)
    total_u = max_u_tiles * uv_width
    total_v = max_v_tiles * uv_height
    
    total_u_with_padding = max_u_tiles * (uv_width + padding) + padding
    total_v_with_padding  = max_v_tiles * (uv_height + padding) + padding
 
    
    if total_u_with_padding > 1.0:

        max_padding = math.ceil(1 - total_u) / (max_u_tiles+1)
        print('The padding forces the v to break, To avoid this use a padding less than: {0}'.format(max_padding))
        
    if total_v_with_padding > 1.0:

        max_padding = math.ceil(1 - total_v) / (max_v_tiles+1)
        print('The padding forces the v to break, To avoid this use a padding less than: {0}'.format(max_padding))

    
    if max_u_tiles < 1 or max_v_tiles < 1:
        pm.warning('The UVs plus the padding does not fit within 0-1 uv space')
        return
    

    u_inc = -1        # local u within a patch
    v_inc = -1        # local v within a patch
    u_offset = -1     # gloabal u
    v_offset = 0      # gloabal v
    
    for index, grp in enumerate(grp_list):
        
        grp_uvs = pm.polyListComponentConversion(grp, tuv=True)
        (u_min, u_max), (v_min, v_max) = pm.polyEvaluate(grp_uvs, boundingBox2d=True)
        
        # when we reach max_u_tiles:
        # reset u_inc and increment v_inc
        if index % max_u_tiles == 0:
            v_inc += 1
            u_inc = 0
            
        # we have not reached max_u_tiles:
        # just increment u_inc
        else:
            u_inc += 1
            
        # if we have reach the maximum number of uv that fits on one patch:
        # reset the v_inc, increment the u_offset
        if index % (max_u_tiles * max_v_tiles) == 0:
            v_inc = 0
            u_offset += 1
            
        if u_offset == 10:
            u_offset = 0
            v_offset += 1
            
        u = (0-u_min) + (uv_width + padding) * u_inc + padding
        v = (0-v_min) + (uv_height + padding) * v_inc + padding
            
        pm.polyEditUV(grp_uvs, u=u+u_offset, v=v+v_offset)
        
'''
#pm.openFile('/Users/johan/Documents/Projects/python_dev/scenes/planes_large_u.mb', f=True)
pm.openFile('/Users/johan/Documents/projects/pojkarna/maya/tendril_anim/scenes/pojk_sc18_120/plane_uv_test.ma', f=True)


padding = 0.0249
grp_list = [pm.PyNode('pPlane{0}'.format(n)) for n in range(20)]

pm.select(grp_list)
tile_uvs(grp_list=grp_list, padding=padding)

'''

def tile_group_uv(grp_list, items_per_row, start_u=0, start_v=0):
    
    tile_list = []
    uv_scale = 1.0/items_per_row
    
    for index, grp in enumerate(grp_list):
                
        # when we have filled one tile create a new list and append to the tile_list
        if index % (items_per_row*items_per_row) is 0:
            temp_list = []
            tile_list.append(temp_list)
            
        #tile_list.append()
        shift_u = (index / (items_per_row*items_per_row))
        
        u_pos = ((index % items_per_row) * uv_scale) + shift_u  + start_u
        v_pos = (((index / items_per_row) % items_per_row) * uv_scale ) + start_v
            
        grp_uvs = pm.polyListComponentConversion(grp, tuv=True)
        temp_list.append({grp.shortName():grp_uvs})
        
        # get the uv min ,max
        (u_min, u_max), (v_min, v_max) = pm.polyEvaluate(grp_uvs, boundingBox2d=True)
        
        #pm.polyEditUV(grp_uvs, v=1, relative=True)
        pm.polyEditUV(grp_uvs, scale=True, scaleU=uv_scale, scaleV=uv_scale)#, pivotU=u_min, pivotV=v_min)
        pm.polyEditUV(grp_uvs, u=u_pos, v=v_pos)
     
    return tile_list


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    

# custom data
class MyCustomType(object):
    
    def __init__(self, data):
        self.data = data
        
           
class TileGroupUV(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(TileGroupUV, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.setWindowTitle("Tile group UV")
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        self.resize(250,200)
        
        self.tab_widget = QtGui.QTabWidget()
        self.vertical_layout.addWidget(self.tab_widget)
        
        ########################
        # tab 1
        ########################
        
        tab_1 = QtGui.QWidget()
        self.tab_widget.addTab(tab_1, "Tile square uv")  
        
        # vertical layout
        tab_1_vertical_layout = QtGui.QVBoxLayout(tab_1) 
        
        
        
        # resize uv group box
        self.resize_uv_group_box = QtGui.QGroupBox("Resize uv")
        tab_1_vertical_layout.addWidget(self.resize_uv_group_box)
        self.resize_uv_group_box.setCheckable(True)
        resize_uv_group_box_layout = QtGui.QVBoxLayout()
        self.resize_uv_group_box.setLayout(resize_uv_group_box_layout) 
        self.items_per_row_spinbox = TileGroupUV.add_spinbox(label='Items per row', min=1, layout=resize_uv_group_box_layout, default=3)

        
        
        
        # options
       
        self.u_start_spinbox = TileGroupUV.add_spinbox(label='U start', layout=tab_1_vertical_layout, double_spinbox=True)
        self.v_start_spinbox = TileGroupUV.add_spinbox(label='V start', layout=tab_1_vertical_layout, double_spinbox=True)
        self.padding_spinbox = TileGroupUV.add_spinbox(label='Padding', layout=tab_1_vertical_layout, double_spinbox=True)
        
        
        
        # button
        tab_1_vertical_layout.addStretch()
        tile_uvs_horiz_layout = QtGui.QHBoxLayout()
        tab_1_vertical_layout.addLayout(tile_uvs_horiz_layout)
        
        self.tile_uvs_button = QtGui.QPushButton('Tile UVs')
        self.tile_uvs_button.setMinimumWidth(100)
        tile_uvs_horiz_layout.addStretch()
        tile_uvs_horiz_layout.addWidget(self.tile_uvs_button)
        self.tile_uvs_button.clicked.connect(self.tile_uvs_button_clicked)
        
        
      
        
        ########################
        # tab 2
        ########################
        
        # vertical layout
        
        tab_2 = QtGui.QWidget()
        self.tab_widget.addTab(tab_2, "Select UVs")
        
        tab_2_vertical_layout = QtGui.QVBoxLayout(tab_2)
          
        
        # tree view
        self.model = QtGui.QStandardItemModel()
        
        self.tree_view = QtGui.QTreeView()
        self.tree_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tree_view.setAlternatingRowColors(True)
 
        
        self.tree_view.setModel(self.model)
        tab_2_vertical_layout.addWidget(self.tree_view)
        
        self.model.setHorizontalHeaderLabels(['UV Tiles'])
        
        # button
        select_tile_horiz_layout = QtGui.QHBoxLayout()
        tab_2_vertical_layout.addLayout(select_tile_horiz_layout)
        
        self.select_tile_button = QtGui.QPushButton('Select UVs')
        self.select_tile_button.setMinimumWidth(50)
        
        select_tile_horiz_layout.addWidget(self.select_tile_button)
        select_tile_horiz_layout.addStretch()
        self.select_tile_button.clicked.connect(self.select_tile_button_clicked)
        

        
    def tile_uvs_button_clicked(self):

        resize_uv = self.resize_uv_group_box.isChecked()
        u_start = self.u_start_spinbox.value()
        v_start = self.v_start_spinbox.value()
        padding = self.padding_spinbox.value()
        
        
        
        # Resize the uvs to fit on the row
        if resize_uv:
            
            items_per_row = self.items_per_row_spinbox.value()
            
            print('Yupp', items_per_row, u_start, v_start, padding)
            return
            
            
            
            
            
            
        
        # do not resize, calculate how many shels that can fit per width / height
        else:
            
            print('Not', u_start, v_start, padding)
            return
    




        grp_list = pm.ls(sl=True)
        
        if not grp_list:
            pm.warning('Nothing is selected!')
            return
            
       # make sure that we have selected transforms
        
        with pm.UndoChunk():
            main_tile_list = tile_group_uv(grp_list=grp_list, items_per_row=items_per_row, start_u=u_start, start_v=v_start)
        
        
        
        
        # populate the model
        
        # clear the model
        self.model.removeRows(0, self.model.rowCount())
        
        for index, tile_list in enumerate(main_tile_list):
              
            item = QtGui.QStandardItem('Patch {0}'.format(index))
            main_uv_list = []
            
            # set flags
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            

            for row_index, tile_dict in enumerate(tile_list):
                
                
                grp_name = tile_dict.keys()[0]
                uv_map = tile_dict.get(grp_name)
                main_uv_list.extend(uv_map)
                
                
                child_item = QtGui.QStandardItem(grp_name)
                
                
                custom_data = MyCustomType(uv_map)
                
                child_item.setData(custom_data, QtCore.Qt.UserRole + 1)

                item.setChild(row_index, 0, child_item)


        
            custom_data = MyCustomType(main_uv_list)
            item.setData(custom_data, QtCore.Qt.UserRole + 1)
            
            self.model.appendRow(item)

            
    
    def select_tile_button_clicked(self):
        
        root = self.model.invisibleRootItem()
        num_rows = self.model.rowCount()
        selection_model = self.tree_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()
                
        sel_uv_list = []
        for row_index in range(num_rows):
            
            item = root.child(row_index)
            q_index = item.index()
            num_children = item.rowCount()
            
            # the parent item is selected
            if q_index in selected_indexes:
                #print('add the parent, containing all sub items')
                
                data = item.data(QtCore.Qt.UserRole + 1)
                sel_uv_list.append(data.data)
                #sel_uv_list.append('PARENT')
                continue
                
            # the parent item is not selected, check if the
            # child item is selected and if so add to sel_list
            else:
                for n in range(num_children):
                    child = item.child(n)
                    if child.index() in selected_indexes:
                        data = child.data(QtCore.Qt.UserRole + 1)
                        sel_uv_list.append(data.data)
                        #sel_uv_list.append(child.text())
                
        pprint.pprint(sel_uv_list)
        pm.select(deselect=True)
        pm.select(sel_uv_list, add=True)
        
           
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
            spinbox.setMinimum(max)
        if default:
            spinbox.setValue(default)
              
        horiz_layout.addWidget(spinbox)
        spinbox.setMinimumWidth(100)
        
        return spinbox
        
def show():      
    win = TileGroupUV(parent=maya_main_window())
    win.show()
           


try:
    win.close()
    
except NameError:
    print('No win to close')

win = TileGroupUV(parent=maya_main_window())
win.show()

#win.add_joint_ref_click()

win.move(150,250)


'''       
pm.openFile('/Users/johan/Documents/Projects/python_dev/scenes/uv_cube.mb', f=True)

grp_list = [pm.PyNode('|group{0}'.format(n)) for n in range(15)]
#pm.select(grp_list)
#tile_list = tile_group_uv(grp_list=grp_list, items_per_row=2, start_u=0, start_v=0)

pm.select(grp_list)
win.tile_uvs_button_clicked()
'''



'''

padding = .025
grp_list = [pm.PyNode('pPlane{0}'.format(n)) for n in range(5)]


tile_uvs(grp_list=grp_list, padding=padding)



'''
