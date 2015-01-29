import maya.cmds as cmds
import pymel.core as pm

class Gradient_attr_ctrl():
    
    def __init__(self): 
       
        pm.window( title='Set multiple gradient attr' )
        layout = pm.columnLayout(rowSpacing=3)
        
        self.gradient_ctrl = pm.gradientControlNoAttr('falloffCurve', w=400, h=200, parent=layout)
        self.gradient_ctrl.setAsString('0,0,2, 1,.5,2, 0,1,2')

        self.relative_cb = pm.checkBoxGrp(label = "Relative",  parent=layout)
        #self.use_channelbox_cb = pm.checkBoxGrp(label = "Use channelbox",  parent=layout, changeCommand1=self.use_cb_toggled)
        
        self.attr_field = pm.textFieldGrp(label='Attribute', text='ty', parent=layout)
        
        self.scale_slider = pm.floatSliderGrp( label='Scale', field=True, value=1, parent=layout)
        
        pm.rowLayout(numberOfColumns=2, columnAlign=(1, 'right'), columnWidth2=(140, 200), parent=layout)
        cmds.text(label='Map curve to same attr', align='right', width=138) #, backgroundColor=(1,.5,.5))
        single_attr_btn = pm.button(label="on multiple objects", command=self.single_attr_btn_pressed, w=150)
        
        pm.rowLayout(numberOfColumns=2, columnAlign=(1, 'right'), columnWidth2=(140, 200), parent=layout)
        cmds.text(label='Map curve to multi attr', align='right', width=138)
        varying_attr_btn = pm.button(label="on one object", command=self.varying_attr_btn_pressed, w=150)

        pm.rowLayout(numberOfColumns=2, columnAlign=(1, 'right'), columnWidth2=(140, 200), parent=layout)
        cmds.text(label='Map curve to same attr', align='right', width=138)
        varying_attr_btn = pm.button(label="on multi components", command=self.components_btn_pressed, w=150)
        
        pm.showWindow()
        
    '''
    def use_cb_toggled(self, *args):
        
        if self.use_channelbox_cb.getValue1():
            self.attr_field.editable = False
            #print('false')
            
        else:
            self.attr_field.editable = True
            #print('true')
    '''
        
    def single_attr_btn_pressed(self, *args):
        
        sel_list = pm.ls(sl=True)
        
        if len(sel_list) < 1:
            pm.warning('Nothing is selected')
            return
        
        num_sel = len(sel_list)
        
        if num_sel is 1:
            inc = 0
            
        else:  
            inc = 1.0 / (num_sel-1)

        attr = self.attr_field.getText()
        scale = self.scale_slider.getValue()
        relative = self.relative_cb.getValue1()
        
        
        for index, sel in enumerate(sel_list):
            
            # get the value at point, use cmds, pm version gives me an error
            value = cmds.gradientControlNoAttr(self.gradient_ctrl, q=True, valueAtPoint=index * inc)
            
            # relative
            if relative:
                
                try:
                    old = pm.getAttr('{0}.{1}'.format(sel_list[index], attr))
                    pm.setAttr('{0}.{1}'.format(sel_list[index], attr), (old + value*scale))
                    
                except pm.MayaAttributeError as e:
                    print(e)
                
            
            # absolute   
            else:
                try:
                    pm.setAttr('{0}.{1}'.format(sel_list[index], attr), value*scale)
                    print(value*scale, index * inc)
                    
                except pm.MayaAttributeError as e:
                    print(e)
                    
                        
    def components_btn_pressed(self, *args):
        
        #sel_list = pm.ls(sl=True)
        sel_list = pm.ls(sl=True, flatten=True)
        
        if len(sel_list) < 1:
            pm.warning('Nothing is selected')
            return
        
        num_sel = len(sel_list)
        print(num_sel)
        
        if num_sel is 1:
            inc = 0
            
        else:  
            inc = 1.0 / (num_sel-1)

        attr = self.attr_field.getText()
        scale = self.scale_slider.getValue()
        relative = self.relative_cb.getValue1()
        
        '''
        use_x = False
        use_y = False
        use_z = False
        
        if attr is 'x':
            use_x = True
            
        if attr is 'y':
            use_y = True
            
        if attr is 'z':
            use_z = True
        '''
        
        for index, sel in enumerate(sel_list):
            
            # get the value at point, use cmds, pm version gives me an error
            value = cmds.gradientControlNoAttr(self.gradient_ctrl, q=True, valueAtPoint=index * inc)
            
                
            try:
                if relative:
                    pm.move(sel, value*scale, os=True, relative=True, z=True)
                else:
                    pm.move(sel, value*scale, os=True, absolute=True, z=True)
                
            except pm.MayaAttributeError as e:
                print(e)
                
                 
                        
    def varying_attr_btn_pressed(self, *args):
    
        sel_list = pm.ls(sl=True)
        
        if len(sel_list) < 1:
            pm.warning('Nothing is selected')
            return
            
        sel_attr_list = pm.channelBox('mainChannelBox', q=True, sma=True)
        obj = sel_list[0]
        
        num_sel = len(sel_attr_list)
        
        if num_sel is 1:
            inc = 0
            
        else:  
            inc = 1.0 / (num_sel-1)

        scale = self.scale_slider.getValue()
        relative = self.relative_cb.getValue1()
    
        for index, attr in enumerate(sel_attr_list):
            
            # get the value at point, use cmds, pm version gives me an error
            value = cmds.gradientControlNoAttr(self.gradient_ctrl, q=True, valueAtPoint=index * inc)
            
            # relative
            if relative:
                
                try:
                    old = pm.getAttr('{0}.{1}'.format(obj, sel_attr_list[index]))
                    pm.setAttr('{0}.{1}'.format(obj, sel_attr_list[index]), (old + value*scale))
                    
                except pm.MayaAttributeError as e:
                    print(e)
                
            
            # absolute   
            else:
                try:
                    pm.setAttr('{0}.{1}'.format(obj, sel_attr_list[index]), (value*scale))
                    #print(index * inc)
                    
                except pm.MayaAttributeError as e:
                    print(e)            
            
                    
                           

gac = Gradient_attr_ctrl()



