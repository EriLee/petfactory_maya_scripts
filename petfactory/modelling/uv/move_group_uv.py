from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
import pprint


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
        
        self.resize(300,100)
        self.setWindowTitle("Tile group UV")
        
        # main vertical layout
        self.vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(self.vertical_layout)
        
        # options
        self.items_per_row_spinbox = TileGroupUV.add_spinbox('Items per row', self.vertical_layout, default=3)
        self.u_start_spinbox = TileGroupUV.add_spinbox('U start', self.vertical_layout)
        self.v_start_spinbox = TileGroupUV.add_spinbox('V start', self.vertical_layout)
        
        # button
        tile_uvs_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(tile_uvs_horiz_layout)
        
        self.tile_uvs_button = QtGui.QPushButton('Tile UVs')
        self.tile_uvs_button.setMinimumWidth(100)
        tile_uvs_horiz_layout.addStretch()
        tile_uvs_horiz_layout.addWidget(self.tile_uvs_button)
        self.tile_uvs_button.clicked.connect(self.tile_uvs_button_clicked)
        
        
        # tree view
        self.model = QtGui.QStandardItemModel()
        
        self.tree_view = QtGui.QTreeView()
        self.tree_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tree_view.setAlternatingRowColors(True)
 
        
        self.tree_view.setModel(self.model)
        self.vertical_layout.addWidget(self.tree_view)
        
        self.model.setHorizontalHeaderLabels(['UV Tiles'])
        
        # button
        select_tile_horiz_layout = QtGui.QHBoxLayout()
        self.vertical_layout.addLayout(select_tile_horiz_layout)
        
        self.select_tile_button = QtGui.QPushButton('Select')
        self.select_tile_button.setMinimumWidth(50)
        
        select_tile_horiz_layout.addWidget(self.select_tile_button)
        select_tile_horiz_layout.addStretch()
        self.select_tile_button.clicked.connect(self.select_tile_button_clicked)
        
 
        
    def tile_uvs_button_clicked(self):
        
        grp_list = pm.ls(sl=True)
        
        if not grp_list:
            pm.warning('Nothing is selected!')
            return
            
        items_per_row = self.items_per_row_spinbox.value()
        u_start = self.u_start_spinbox.value()
        v_start = self.v_start_spinbox.value()
        
        main_tile_list = tile_group_uv(grp_list=grp_list, items_per_row=items_per_row, start_u=u_start, start_v=v_start)
        

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
        
def show():      
    win = TileGroupUV(parent=maya_main_window())
    win.show()
           

'''
try:
    win.close()
    
except NameError:
    print('No win to close')

win = TileGroupUV(parent=maya_main_window())
win.show()

#win.add_joint_ref_click()

win.move(150,250)

        
pm.openFile('/Users/johan/Documents/Projects/python_dev/scenes/uv_cube.mb', f=True)

grp_list = [pm.PyNode('|group{0}'.format(n)) for n in range(15)]
#pm.select(grp_list)
#tile_list = tile_group_uv(grp_list=grp_list, items_per_row=2, start_u=0, start_v=0)

pm.select(grp_list)
win.tile_uvs_button_clicked()
'''