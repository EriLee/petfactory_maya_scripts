import sys, os
from PySide import QtGui, QtCore
import pymel.core as pm
from shiboken import wrapInstance
import maya.OpenMayaUI as omui

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    

# custom data
class MyCustomType(object):
    
    def __init__(self, data):
        self.data = data
        
class MaterialItem(QtGui.QStandardItem):
    pass

class MeshParentItem(QtGui.QStandardItem):
    pass

class FaceParentItem(QtGui.QStandardItem):
    pass

class MeshItem(QtGui.QStandardItem):
    pass

class FaceItem(QtGui.QStandardItem):
    pass
                 
class DeselectableTreeView(QtGui.QTreeView):
    
    # deselect when clicked outside the items
    def mousePressEvent(self, event):
        self.clearSelection()
        QtGui.QTreeView.mousePressEvent(self, event)
        
    # disable double click rename
    def edit(self, index, trigger, event):
        if trigger == QtGui.QAbstractItemView.DoubleClicked:
            #print 'DoubleClick Killed!'
            return False
        return QtGui.QTreeView.edit(self, index, trigger, event)

class Example(QtGui.QWidget):

    def __init__(self, parent):
        super(Example, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.initUI()

    def initUI(self):      
        
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('Tree View')
        self.click_function = None;

        # layout
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setContentsMargins(6,6,6,6)

        # model
        self.model = QtGui.QStandardItemModel()
        self.proxy_model = QtGui.QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.model.setColumnCount (3);
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, "Material");
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Mesh");
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "Face");
        
        # tree view
        self.tree_view = DeselectableTreeView()
        self.tree_view.clicked.connect(self.item_clicked)
        self.tree_view.setModel(self.proxy_model)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setModel(self.model)
        self.layout.addWidget(self.tree_view)

        #self.show()
     
      
    def item_clicked(self):

        child_list = []

        if(self.tree_view.selectionModel().hasSelection()):
            for index in self.tree_view.selectedIndexes():
                item = self.model.itemFromIndex(index)

                # Mat main parent
                if isinstance(item, MaterialItem):
                    # get the child items
                    for i in range(item.rowCount()):
                        mat_child = item.child(i)
                        for j in range(mat_child.rowCount()):
                            child_list.append(mat_child.child(j))

                # Mesh group parent
                elif isinstance(item, MeshParentItem):
                    #print('MESH')
                    for i in range(item.rowCount()):
                        child_list.append(item.child(i))

                # Face group paerent
                elif isinstance(item, FaceParentItem):
                    #print('FACE')
                    for i in range(item.rowCount()):
                        child_list.append(item.child(i))

                # bottom level mesh or face
                elif isinstance(item, MeshItem):
                    child_list.append(item)

                elif isinstance(item, FaceItem):
                    child_list.append(item)  
                    
                    
        data_list = []
        
        for x in child_list:
            
            data = x.data(QtCore.Qt.UserRole + 1)
            
            if isinstance(data, MyCustomType): 
                print(data.data)
                data_list.append(data.data)
                
            else:
                print(data)

        # if we have a click function defined run it with data as param
        if self.click_function is not None:
            self.click_function(data_list)
     
                    
    def populate_model(self, mat_dict):
        
        # the root item
        root_item = self.model.invisibleRootItem()
        
        # index to be used to reference the row when creating the mat items
        row_index = 0

        for mat_name, info_dict in sorted(mat_dict.iteritems()):
            
            mesh_list = info_dict.get('mesh')
            face_list = info_dict.get('face')
            
            # if the mat is not assigned to any mesh or face, continue
            if len(mesh_list) < 1 and len(face_list) < 1:
                continue

            # create the material parent item 
            mat_item = MaterialItem(mat_name)
            root_item.appendRow(mat_item)


            if len(mesh_list) > 0:
                mesh_parent = MeshParentItem('mesh')
                mat_item.appendRow(mesh_parent)
                
            if len(face_list) > 0:
                face_parent = FaceParentItem('face')
                mat_item.appendRow(face_parent)
            
            # add the info of the number of assigned meshes and facees
            self.model.setItem(row_index, 1, QtGui.QStandardItem(str(len(mesh_list))))
            self.model.setItem(row_index, 2, QtGui.QStandardItem(str(len(face_list))))
           
            for index, mesh in enumerate(mesh_list):
                mesh_item = MeshItem('mesh {0}'.format(index))
                custom_data = MyCustomType(mesh)
                mesh_item.setData(custom_data, QtCore.Qt.UserRole + 1)
                mesh_parent.appendRow(mesh_item)
            
            for index, face in enumerate(face_list):
                face_item = FaceItem('face {0}'.format(index))
                custom_data = MyCustomType(face)
                face_item.setData(custom_data, QtCore.Qt.UserRole + 1)
                face_parent.appendRow(face_item)
     
            row_index += 1
                           

def custom_click_function(data):
    pm.select(data)
    
def get_dict(mat_list):
    
    ret_dict = {}
    
    for mat in mat_list:
        
        if (mat == 'lambert1' or mat == 'particleCloud1'): continue
        
        # get the shading group
        sg_list = mat.listConnections(type='shadingEngine')
        
        mesh_list = []
        face_list = []
        
        ret_dict.update({mat.name():{'mesh':mesh_list, 'face':face_list}})
        
        # loop through the sg looking for menbers
        for sg in sg_list:
            
            member_list = sg.members(flatten=True)
            
            # loop through the members, check it the mat is assigned to faces or meshes
            for member in member_list:
    
                if type(member) == pm.nodetypes.Mesh:
                    #print('mashhh')
                    mesh_list.append(member)
                    
                elif type(member) == pm.general.MeshFace:
                    #print('face')
                    face_list.append(member)
                
    return ret_dict


def show():
    mat_list = pm.ls(mat=True)
    d = get_dict(mat_list)
    
    ex = Example(parent=maya_main_window())
    ex.populate_model(d)
    ex.click_function = custom_click_function
    ex.show()
    #d = {"mat_1":{"mesh":[MyCustomType(cube)],"face":[MyCustomType(cube)]}}
    


#show()
