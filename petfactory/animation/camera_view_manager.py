import pymel.core as pm


class CameraViewManager(object):
    
    def __init__(self):
        
        self.camera = None
        self.camera_shape = None
        self.zoom = 1
        self.horizontal_pan = 0
        self.vertical_pan = 0
        self.overscan = 1.3
    
        
    def set_zoom(self, zoom):
        
        self.zoom = zoom
        self.set_pan_zoom()
        
    
    def set_pan(self, h_pan, v_pan):
        
        self.horizontal_pan = h_pan
        self.vertical_pan = v_pan
        
    
    def set_camera(self, camera):
        
        self.camera = camera
        self.camera_shape = camera.getShape()
    
    def toggle_pan_zoom(self):
        
        self.camera_shape.panZoomEnabled.set(not cam_shape.panZoomEnabled.get())

        
    def copy_pan_zoom_from_camera(self):
        
        self.zoom = self.camera_shape.zoom.get()
        self.horizontal_pan = self.camera_shape.horizontalPan.get()
        self.vertical_pan = self.camera_shape.verticalPan.get()
        
        
    def set_pan_zoom(self):
        self.camera_shape.zoom.set(self.zoom)
        self.camera_shape.horizontalPan.set(self.horizontal_pan)
        self.camera_shape.verticalPan.set(self.vertical_pan)
        

    def toggle_resolution_gate(self):
        
        if cam_shape.displayResolution.get():
            
            self.camera_shape.displayResolution.set(False)
            self.camera_shape.overscan.set(1.0)
            
        else:
            self.camera_shape.displayResolution.set(True)
            self.camera_shape.overscan.set(self.overscan)
              
        
    def set_overscan(self, overscan):
        
        self.overscan = overscan
        
    def set_gate_mask_color(self, color):
        
        self.camera_shape.displayGateMaskColor.set(color)
        
        

cam = pm.PyNode('camera2')
        
cvm = CameraViewManager()
cvm.set_camera(cam)
cvm.copy_pan_zoom_from_camera()


#cvm.set_zoom(2)
cvm.toggle_pan_zoom()

cvm.toggle_resolution_gate()

cvm.set_gate_mask_color((.3,.3,.3))

        

    
    
    