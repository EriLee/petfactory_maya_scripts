from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
import pprint
import math, random

#import petfactory.util.dev as dev

'''
Let the user worry about the padding etc?
just tile the number of specified shells?

add a pre estimate number of shells in u and v?
and margin estimate.

'''


# delete transforms
#dev.del_transform()

def udim_from_index(num_items_u, num_items_v, num_items, start_index=0, num_random=None):
    '''returns a dict with the UDIM number as key and a list of uv values as the value.
    Note that the uvs are in the form of a grid in that we can only pass in integers that 
    defines the number of items in each direction (u and v) and based on those numbers it
    creates a "grid" with the first value at uv (0,0).'''

    num_items_per_patch = num_items_u * num_items_v
    max_patches_u = 10

    udim_dict = {}
    for index in range(start_index, (num_items + start_index)):
        
        # if num_random is specified (int) set the index to be a random
        # number between start_index -> start_index + num_random
        if num_random is not None:
            index = start_index + random.randint(0, (num_random-1))
            
        # local uv (to each patch)
        local_u = (index % num_items_u) / float(num_items_u)
        local_v = ((index / num_items_u) % num_items_v) / float(num_items_v)
        
        #print(local_u, local_v)
        
        # patch index
        patch_index_u = (index / num_items_per_patch) % max_patches_u
        patch_index_v = index / (num_items_per_patch * max_patches_u)
        
        u = patch_index_u + local_u
        v = patch_index_v + local_v
                
        udim = 1000 + (patch_index_u + 1) + (max_patches_u * patch_index_v)

        # create a key in the dict using the udim
        if udim not in udim_dict:
            udim_dict[udim] = []

        udim_dict[udim].append((u,v))
                
    return udim_dict


def set_uvs(node_list, num_items_u, num_items_v, spacing=0, left_offset=0, bottom_offset=0, start_index=0, num_random=None):
    
    (u_min, u_max), (v_min, v_max) = pm.polyEvaluate(pm.polyListComponentConversion(node_list[0], tuv=True), boundingBox2d=True)
    uv_width = u_max - u_min
    uv_height = v_max - v_min
    
    max_num_items_u = int(math.floor(1.0 / uv_width))
    max_num_items_v = int(math.floor(1.0 / uv_height))
    #print(max_num_items_u, max_num_items_v)
    
    
    #spacing = .03
    #left_offset = .02
    #bottom_offset = .02
    
    
    num_items = len(node_list)
    
    # hardcoded values, change later
    #num_items_u = 4
    #num_items_v = 4
    num_items_per_patch = num_items_u * num_items_v
    #start_index = 0
    #num_random = None
    
    udim_dict = udim_from_index(num_items_u=num_items_u, num_items_v=num_items_v, num_items=num_items, start_index=start_index, num_random=num_random)
    #pprint.pprint(uv_dict)
    
    # step through the udim dict. The dict has the udim as keys with a list of the uv coords as value
    # note that the uvs are returned in the uv list as a uniform grid.
    index = 0
    for udim in sorted(udim_dict):
        
        # iterate through the uv_list
        for uv in (udim_dict[udim]):
                                    
            node_uvs = pm.polyListComponentConversion(node_list[index], tuv=True)
            (u_min, u_max), (v_min, v_max) = pm.polyEvaluate(node_uvs, boundingBox2d=True)
            
            # the uv are stored in a uniform grid, i.e. if we have 4 shells on one u row
            # the uv stored in the uv list will be [0, 25, 5, 75] on patch u 0 v 0
            # on patch u1 v0 it will be [1.0, 1.25, 1.5, 1.75]
            # here get the remainder of the uv to get the "fraction part"
            # this will later be used to multiply with the combined width all the uv shells per row.
            percent_u = uv[0] % 1
            percent_v = uv[1] % 1
            
            # here we get the patch "index" i.e. which patch we are on. this will be used to offset the
            # local uv shell to the global "position"
            patch_u = math.floor(uv[0] / 1.0)
            patch_v = math.floor(uv[1] / 1.0)
            
            spacing_u = spacing * (percent_u * num_items_u)
            spacing_v = spacing * (percent_v * num_items_v)
            
            u = -u_min + percent_u * (uv_width * num_items_u) + patch_u + spacing_u + left_offset
            v = -v_min + percent_v * (uv_height * num_items_v) + patch_v + spacing_v + bottom_offset
            
            pm.polyEditUV(node_uvs, u=u, v=v)
                                   
            index += 1



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
        self.tab_widget.addTab(tab_1, "Tile uvs")  
        
        # vertical layout
        tab_1_vertical_layout = QtGui.QVBoxLayout(tab_1) 
        
        
        # options
        self.num_u_spinbox = TileGroupUV.add_spinbox(label='U Num items', layout=tab_1_vertical_layout, min=1, max=999, default=4)
        self.num_v_spinbox = TileGroupUV.add_spinbox(label='V Num items', layout=tab_1_vertical_layout, min=1, max=999, default=4)
        self.spacing_spinbox = TileGroupUV.add_spinbox(label='Spacing', layout=tab_1_vertical_layout, double_spinbox=True, decimals=4)
        self.left_offset_spinbox = TileGroupUV.add_spinbox(label='Left offset', layout=tab_1_vertical_layout, double_spinbox=True, decimals=4)
        self.bottom_offset_spinbox = TileGroupUV.add_spinbox(label='Bottom offset', layout=tab_1_vertical_layout, double_spinbox=True, decimals=4)
        
        # use existing hairsystem group box
        self.randomize_groupbox = QtGui.QGroupBox("Randomize")
        
        tab_1_vertical_layout.addWidget(self.randomize_groupbox)
        self.randomize_groupbox.setCheckable(True)
        self.randomize_groupbox.setChecked(False)
        randomize_groupbox_vert_layout = QtGui.QVBoxLayout()
        self.randomize_groupbox.setLayout(randomize_groupbox_vert_layout)
        
        self.max_random_index_spinbox = TileGroupUV.add_spinbox(label='Max random index', layout=randomize_groupbox_vert_layout, min=1, max=999, default=16)
  
        
        
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

        num_items_u = self.num_u_spinbox.value()
        num_items_v = self.num_v_spinbox.value()
        left_offset = self.left_offset_spinbox.value()
        bottom_offset = self.bottom_offset_spinbox.value()
        randomize = self.randomize_groupbox.isChecked()
        num_random = None
        spacing = self.spacing_spinbox.value()
        start_index = 0
        
        if randomize:
            num_random = self.max_random_index_spinbox.value()
            print(num_random)
            

        print(num_items_u, num_items_v, left_offset, bottom_offset, randomize, num_random, spacing, start_index)
        
        node_list = pm.ls(sl=True)
        
        if not node_list:
            pm.warning('Nothing is selected!')
            return
            
       # make sure that we have selected transforms
        
        with pm.UndoChunk():
            
            # node_list, num_items_u, num_items_v, spacing=0, left_offset=0, bottom_offset=0, start_index=0, num_random=None):
            set_uvs(node_list, num_items_u, num_items_v, spacing, left_offset, bottom_offset, start_index, num_random)
             
        '''
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
        '''

            
    
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
    def add_spinbox(label, layout, min=None, max=None, default=None, double_spinbox=False, decimals=3):
        
        horiz_layout = QtGui.QHBoxLayout()
        layout.addLayout(horiz_layout)

        label = QtGui.QLabel(label)
        label.setMinimumWidth(100)
        horiz_layout.addWidget(label)
        
        horiz_layout.addStretch()
        
        if double_spinbox:
            spinbox = QtGui.QDoubleSpinBox()
            spinbox.setDecimals(decimals)

        else:
            spinbox = QtGui.QSpinBox()
        
        if min:
            spinbox.setMinimum(min)
        if max:
            spinbox.setMaximum(max)
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


win.move(150,250)

            
pm.openFile("/Users/johan/Documents/Projects/python_dev/scenes/plane_grid.mb", f=True)
#node_list = [pm.PyNode('pPlane{0}'.format(n+1)) for n in range(128)]
#pm.select(node_list)



       

