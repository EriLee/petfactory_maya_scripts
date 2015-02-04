from PySide import QtCore, QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm

import petfactory.rigging.tendril_rig.tendril_setup as tendril_setup
import petfactory.rigging.ribbon.create_ribbon as create_ribbon

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    
    
class TendrilSetupWidget(QtGui.QWidget):
 
    def __init__(self, parent=None):
 
        super(TendrilSetupWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.resize(300,100)
        self.setWindowTitle("Tendril Setup")

 
        # layout
        vertical_layout = QtGui.QVBoxLayout()
        self.setLayout(vertical_layout)
        
        tab_widget = QtGui.QTabWidget()
        vertical_layout.addWidget(tab_widget)
        

        
        # tab widgts and layout
        # tab 1        
        tab_1 = QtGui.QWidget()
        tab_widget.addTab(tab_1, "Setup rig")  
        tab_1_vertical_layout = QtGui.QVBoxLayout(tab_1)
        
        # tab 1  
        tab_2 = QtGui.QWidget()
        tab_widget.addTab(tab_2, "Edit")  
        tab_2_vertical_layout = QtGui.QVBoxLayout(tab_2) 




        # tendril name
        self.name_horiz_layout = QtGui.QHBoxLayout()
        tab_1_vertical_layout.addLayout(self.name_horiz_layout)
        
        self.name_label = QtGui.QLabel('Tendril Name')
        self.name_horiz_layout.addWidget(self.name_label)
        
        self.name_line_edit = QtGui.QLineEdit()
        self.name_horiz_layout.addWidget(self.name_line_edit)
          
        # tree view
        self.model = QtGui.QStandardItemModel()
        
        self.tree_view = QtGui.QTreeView()
        self.tree_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tree_view.setAlternatingRowColors(True)
 

        self.tree_view.setModel(self.model)
        tab_1_vertical_layout.addWidget(self.tree_view)
        
        self.model.setHorizontalHeaderLabels(['Ref Group', 'Name'])
                
        # add joint ref
        self.joint_ref_horiz_layout = QtGui.QHBoxLayout()
        tab_1_vertical_layout.addLayout(self.joint_ref_horiz_layout)        
        
        # add
        self.add_joint_ref_button = QtGui.QPushButton(' + ')
        self.add_joint_ref_button.setMinimumWidth(40)
        
        self.joint_ref_horiz_layout.addWidget(self.add_joint_ref_button)
        self.add_joint_ref_button.clicked.connect(self.add_joint_ref_click)
        
        # remove
        self.remove_joint_ref_button = QtGui.QPushButton(' - ')
        self.remove_joint_ref_button.setMinimumWidth(40)
        
        self.joint_ref_horiz_layout.addWidget(self.remove_joint_ref_button)
        self.remove_joint_ref_button.clicked.connect(self.remove_joint_ref_click)
        
        self.joint_ref_label = QtGui.QLabel('Add / remove joint ref group')
        self.joint_ref_horiz_layout.addWidget(self.joint_ref_label)
        self.joint_ref_horiz_layout.addStretch()
        

        
        # hairsystem group box
        hairsystem_group_box = QtGui.QGroupBox("Hairsystem")
        tab_1_vertical_layout.addWidget(hairsystem_group_box)
        hairsystem_group_vert_layout = QtGui.QVBoxLayout()
        hairsystem_group_box.setLayout(hairsystem_group_vert_layout)
        
        # use existing hairsystem group box
        self.use_existing_group_box = QtGui.QGroupBox("Use existing")
        
        hairsystem_group_vert_layout.addWidget(self.use_existing_group_box)
        self.use_existing_group_box.setCheckable(True)
        self.use_existing_group_box.setChecked(False)
        use_existing_group_box_vert_layout = QtGui.QVBoxLayout()
        self.use_existing_group_box.setLayout(use_existing_group_box_vert_layout)
        self.use_existing_group_box.clicked.connect(self.hairsystem_groupbox_clicked)

        # use existing hairsystem widget
        self.use_existing_hairsystem_widget = QtGui.QWidget()
        
        # use existing hairsystem
        use_existing_group_box_vert_layout.addWidget(self.use_existing_hairsystem_widget)

        use_existing_hairsystem_horiz_layout = QtGui.QHBoxLayout()
        
        self.use_existing_hairsystem_widget.setLayout(use_existing_hairsystem_horiz_layout)
        
        add_existing_hairsystem_button = QtGui.QPushButton('Hairsystem >')
        use_existing_hairsystem_horiz_layout.addWidget(add_existing_hairsystem_button)
        add_existing_hairsystem_button.clicked.connect(self.add_hairsystem_clicked)
                
        self.existing_hairsystem_line_edit = QtGui.QLineEdit()
        use_existing_hairsystem_horiz_layout.addWidget(self.existing_hairsystem_line_edit)


        
        # share hairsystem
        # create new hairsystem group box
        self.create_new_group_box = QtGui.QGroupBox("Create new")
        self.create_new_group_box.clicked.connect(self.hairsystem_groupbox_clicked)
        hairsystem_group_vert_layout.addWidget(self.create_new_group_box)
        self.create_new_group_box.setCheckable(True)
        create_new_group_box_vert_layout = QtGui.QVBoxLayout()
        self.create_new_group_box.setLayout(create_new_group_box_vert_layout)
        
        
        
        
        self.share_hairsystem_widget = QtGui.QWidget()

        create_new_group_box_vert_layout.addWidget(self.share_hairsystem_widget)

        
        share_hairsystem_horiz_layout = QtGui.QHBoxLayout()
        self.share_hairsystem_widget.setLayout(share_hairsystem_horiz_layout)

        self.share_hairsystem_checkbox = QtGui.QCheckBox()
        share_hairsystem_horiz_layout.addWidget(self.share_hairsystem_checkbox)
        
        self.share_hairsystem_label = QtGui.QLabel('Share Hairsystem')
        share_hairsystem_horiz_layout.addWidget(self.share_hairsystem_label)
        share_hairsystem_horiz_layout.addStretch()
        
 

        # Setup
        self.setup_horiz_layout = QtGui.QHBoxLayout()
        tab_1_vertical_layout.addLayout(self.setup_horiz_layout)
        
        self.setup_button = QtGui.QPushButton('Setup Tendrils')
        self.setup_button.setMinimumWidth(125)
        self.setup_horiz_layout.addStretch()
        self.setup_horiz_layout.addWidget(self.setup_button)
        self.setup_button.clicked.connect(self.setup_tendril)
        
        
        
        # edit ui
        copy_cluster_position_button = QtGui.QPushButton('Copy cluster pos')
        copy_cluster_position_button.clicked.connect(self.copy_clust_pos_clicked)
        tab_2_vertical_layout.addWidget(copy_cluster_position_button)
        
        self.bind_mesh_line_edit = QtGui.QLineEdit()
        tab_2_vertical_layout.addWidget(self.bind_mesh_line_edit )

        add_ribbon_button = QtGui.QPushButton('Add ribbon button')
        add_ribbon_button.clicked.connect(self.create_ribbon_for_joint_set)
        tab_2_vertical_layout.addWidget(add_ribbon_button)
        
        tab_2_vertical_layout.addStretch()
        
        

     
    def copy_clust_pos_clicked(self):
        
        sel_list = pm.ls(sl=True)

        if len(sel_list) < 2:
            pm.warning('Please select at least two transform nodes')
            return
            
        try:
            source_cluster_grp = sel_list[0].cluster_grp.get()
            source_cluster_list = source_cluster_grp.listRelatives(ad=True, type='clusterHandle')
            source_cluster_list.sort()

        except AttributeError as e:
            print(e)
            return


        num_sel = len(sel_list)
        index = 1
        while index < num_sel:

            try:
                target_cluster_grp = sel_list[index].cluster_grp.get()
                target_cluster_list = target_cluster_grp.listRelatives(ad=True, type='clusterHandle')
                target_cluster_list.sort()

            except AttributeError as e:
                print(e)
                continue

            #print(target_cluster_list)
            index += 1

            if len(target_cluster_list) != len(source_cluster_list):
                pm.warning('the cluster list is not of the same length, skipping')
                continue

            # the cluster lists are a list of the clusterHandleShapes, we call getParent 
            # method on them to be able set the translation
            for cls_index, source_cluster in enumerate(source_cluster_list):
                target_cluster_list[cls_index].getParent().translate.set(source_cluster.getParent().translate.get())


    def create_ribbon_for_joint_set(self):
        
        mesh_name = self.bind_mesh_line_edit.text()

        # get a ref to the node
        try:
            mesh_node = pm.PyNode(mesh_name)
            
        except pm.general.MayaNodeError as e:
            pm.warning('Not a valid node!', e)
            return
            
        # check that it is a mesh
        try:
            if not isinstance(mesh_node.getShape(), pm.nodetypes.Mesh):
                pm.warning('Not a valid node!', e)
                return
                
        except AttributeError as e:
            pm.warning('Not a valid node!', e)
            return


        sel_list = pm.ls(sl=True)

        width = 35
        depth = 1
        num_u_patches = 10
        num_follicles = 50

        for sel in sel_list:

            main_grp = sel.main_grp.get()
            bind_jnt_grp = sel.bind_jnt_grp.get()


            jnt_list = bind_jnt_grp.listRelatives(allDescendents=True, type='joint')
            jnt_list.sort()


             # build the ribbon surface
            ribbon = create_ribbon.build_ribbon(width=width, depth=depth, num_u_patches=num_u_patches)
            ribbon.setAttr('visibility', 0, lock=True)
            
            # add follicles
            follicle_dict = create_ribbon.add_follicles(nurbs_surface=ribbon, num_follicles=num_follicles)
            follicle_grp = follicle_dict.get('follicle_grp')

            # add joint to the follicles
            follicle_jnt_list = create_ribbon.add_follicle_joints(follicle_dict.get('follicle_transform_list'))
            
            #skinMethod 0 : linear, 1 : dual quaternion
            # ignoreHierarchy : Disregard the place of the joints in the skeleton hierarchy
            pm.skinCluster(jnt_list, ribbon, skinMethod=1, ignoreHierarchy=True)

            # duplicate the mesh
            dup_mesh = pm.duplicate(mesh_node)[0]

            # bind to follicle joints
            pm.skinCluster(follicle_jnt_list, dup_mesh, skinMethod=1, ignoreHierarchy=True)
            
            # organize
            ribbon_grp = pm.group(em=True, n='ribbon_grp')
            pm.parent(ribbon, ribbon_grp)
            pm.parent(follicle_grp, ribbon_grp)
            pm.parent(ribbon_grp, main_grp)

            pm.addAttr(sel, longName='show_ribbon_joints', at="enum", en="off:on", keyable=True)
            sel.show_ribbon_joints >> follicle_grp.visibility

            mesh_grp = pm.group(em=True, n='mesh_grp')
            pm.parent(mesh_grp, main_grp)
            pm.parent(dup_mesh, mesh_grp)


        '''
        sel_list = pm.ls(sl=True)
        
        for sel in sel_list:
            member_list = sel.members()
            member_list.sort()
            
            # build the ribbon surface
            ribbon = create_ribbon.build_ribbon(width=width, depth=depth, num_u_patches=num_u_patches)
            
            # add follicles
            follicle_dict = create_ribbon.add_follicles(nurbs_surface=ribbon, num_follicles=num_follicles)
            
            # add joint to the follicles
            create_ribbon.add_follicle_joints(follicle_dict.get('follicle_transform_list'))
            
            #skinMethod 0 : linear, 1 : dual quaternion
            # ignoreHierarchy : Disregard the place of the joints in the skeleton hierarchy
            pm.skinCluster(member_list, ribbon, skinMethod=1, ignoreHierarchy=True)

        '''
        


    def add_joint_ref_click(self):
        

        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Please select a camera!')
            return

        
        for sel in sel_list:
        
            if not isinstance(sel, pm.nodetypes.Transform):
                pm.warning('{0} is not a valid transform, skipped'.format(sel.name()))
                continue
            
            item = QtGui.QStandardItem(sel.name())
            
            # set flags
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            
            item.setCheckable(True)
            item.setCheckState(QtCore.Qt.Checked)
            self.model.appendRow(item) 
                
    
    def remove_joint_ref_click(self):
        
        selection_model = self.tree_view.selectionModel()
        
        # returns QModelIndex
        selected_rows = selection_model.selectedRows()
        
        row_list = [sel.row() for sel in selected_rows]
        row_list.sort(reverse=True)
        
        for row in row_list:
            self.model.removeRow(row)
            
            
    def hairsystem_groupbox_clicked(self):

        is_checked = self.sender().isChecked()
        
        if self.sender() is self.use_existing_group_box:
            self.create_new_group_box.setChecked(not is_checked)
        
        else:
            self.use_existing_group_box.setChecked(not is_checked)


    def add_hairsystem_clicked(self):
        
        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Select a hairsystem!')
            return
        
        try:

            shape = sel_list[0].getShape()
            
            if isinstance(shape, pm.nodetypes.HairSystem):
                self.existing_hairsystem_line_edit.setText(sel_list[0].longName())
                
            else:
                pm.warning('Select a hairsystem!')
            
        except AttributeError as e:
            pm.warning('Please select a Hairsystem ', e)
            return
            
            
    
    
    
       
    def setup_tendril(self):
        
        ref_grp_list = []
        
        root = self.model.invisibleRootItem()
        num_children = self.model.rowCount()
        
        
        # the ref grp
        if num_children < 1:
            pm.warning('No joint ref are available in the treeview!')
            return
    
        for i in range(num_children):
            
            child = root.child(i)
            
            if child.checkState():
                
                ref_grp_list.append(child.text())
                
                
        # hairsystem        
        use_existing = self.use_existing_group_box.isChecked()
        existing_hairsystem = None
        share_hairsystem = self.share_hairsystem_checkbox.isChecked()
        
        # if we are to use an existing hairsystem, make sure that is is valid, if so get a ref to it
        if use_existing:
            
            existing_hairsystem_name = self.existing_hairsystem_line_edit.text()
            
            try:
                existing_hairsystem = pm.PyNode(existing_hairsystem_name)
                
            except pm.general.MayaNodeError as e:
                pm.warning('The hairsystem specified is not valid')
                return
                
            try:
                
                shape = existing_hairsystem.getShape()
                
                if not isinstance(shape, pm.nodetypes.HairSystem):
                    pm.warning('Please select a Hairsystem')
                    return
                
            except AttributeError as e:
                pm.warning('Please select a Hairsystem ', e)
                return
                
                
                
                
                
        # get the name
        name = self.name_line_edit.text()
        if name == '':
            name = 'tendril'
        
        ref_list = []
        name_list = []
        
        for index, ref_grp in enumerate(ref_grp_list):
            
            ref_list.append(pm.PyNode(ref_grp))
            name_list.append('{0}_{1}'.format(name, index))
            
        
        #print(ref_list, name_list, existing_hairsystem)
        

        # build the joints
        jnt_dict_list = tendril_setup.build_joints(joint_ref_list=ref_list, name_list=name_list)
        
        
        # set up the nhair dynamics
        output_curve_list = []
        
        
        output_curve_set = pm.sets(name='output_curve_set')
        root_ctrl_set = pm.sets(name='root_ctrl_set') 
        sine_anim_ctrl_set = pm.sets(name='sine_anim_ctrl_set') 
        
        output_curve_list = []
        root_ctrl_list = []
        sine_anim_ctrl_list = []

  
        for index, jnt_dict in enumerate(jnt_dict_list):
            
            # use an existing hairsystem
            if use_existing:
                print('use existing hairsystem')
                
                dyn_joint_dict = tendril_setup.setup_dynamic_joint_chain(jnt_dict, ctrl_size=1.2, existing_hairsystem=existing_hairsystem)
                
                
                
                
            # create a new hairsystem  
            else:
                print('create a new hairsystem')
                
                
                
                
                # share the new hairsystem
                if share_hairsystem:
                    print('share the new hairsystem')
                    
                    if index is 0:
                        dyn_joint_dict = tendril_setup.setup_dynamic_joint_chain(jnt_dict, ctrl_size=1.2)
                        hairsystem_0 = dyn_joint_dict.get('hairsystem')
                        
                    else:
                        dyn_joint_dict = tendril_setup.setup_dynamic_joint_chain(jnt_dict, ctrl_size=1.2, existing_hairsystem=hairsystem_0)
                    
    
    
                # do not share the hairsystem    
                else:
                    print('do NOT share the new hairsystem')
                    dyn_joint_dict = tendril_setup.setup_dynamic_joint_chain(jnt_dict, ctrl_size=1.2)
                    


            proc_anim_dict = tendril_setup.add_pocedural_wave_anim(dyn_joint_dict, ctrl_size=1)
            
            output_curve_list.append(dyn_joint_dict.get('output_curve'))
            root_ctrl_list.append(dyn_joint_dict.get('root_ctrl'))
            sine_anim_ctrl_list.append(proc_anim_dict.get('sine_anim_ctrl'))

         
        output_curve_set.addMembers(output_curve_list)
        root_ctrl_set.addMembers(root_ctrl_list)
        sine_anim_ctrl_set.addMembers(sine_anim_ctrl_list)


def show():      
    win = TendrilSetupWidget(parent=maya_main_window())
    win.show()
    


'''
try:
    win.close()
    
except NameError:
    print('No win to close')

win = TendrilSetupWidget(parent=maya_main_window())
win.show()


win.move(100,150)


pm.system.openFile('/Users/johan/Documents/projects/pojkarna/maya/flower_previz/scenes/tendril_design_v005_script_base.mb', f=True)

node = pm.PyNode('rig_ref')
pm.select(node)
win.add_joint_ref_click()
win.add_joint_ref_click()
'''
