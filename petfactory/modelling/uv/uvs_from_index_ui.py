from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
import pprint
import math


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

        #u_start = self.u_start_spinbox.value()
        #v_start = self.v_start_spinbox.value()
        spacing = self.spacing_spinbox.value()

          
        grp_list = pm.ls(sl=True)
        
        if not grp_list:
            pm.warning('Nothing is selected!')
            return
            
       # make sure that we have selected transforms
        
        with pm.UndoChunk():
            #main_tile_list = tile_group_uv(grp_list=grp_list, items_per_row=items_per_row, start_u=u_start, start_v=v_start)
            #main_tile_list = tile_uvs(grp_list=grp_list, padding=padding, u_start=u_start, v_start=v_start)
            pass
            
        
        
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



