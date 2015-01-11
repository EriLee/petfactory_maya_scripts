import pymel.core as pm
import pprint

class CreateCtrl(object):

    _circle_20_cvs = [(0.0, 0.9999999999999998, 0.0),
     (0.0, 0.9510571360588072, -0.3090171813964844),
     (0.0, 0.8090175390243528, -0.5877856016159058),
     (0.0, 0.5877856016159055, -0.8090174794197083),
     (0.0, 0.30901715159416177, -0.9510570168495178),
     (0.0, -2.220446049250313e-16, -1.0000004768371582),
     (0.0, -0.3090171515941622, -0.951056957244873),
     (0.0, -0.5877854824066164, -0.8090173006057739),
     (0.0, -0.8090172410011294, -0.5877854228019714),
     (0.0, -0.9510567784309389, -0.3090170621871948),
     (0.0, -1.0000002384185793, 0.0),
     (0.0, -0.9510567784309389, 0.3090170621871948),
     (0.0, -0.8090171813964846, 0.5877853631973267),
     (0.0, -0.5877853631973269, 0.8090171217918396),
     (0.0, -0.30901706218719505, 0.9510566592216492),
     (0.0, -2.980232260973992e-08, 1.0000001192092896),
     (0.0, 0.30901697278022744, 0.9510565996170044),
     (0.0, 0.5877852439880369, 0.8090170621871948),
     (0.0, 0.8090170025825498, 0.5877853035926819),
     (0.0, 0.9510565400123594, 0.30901700258255005),
     (0.0, 0.9999999999999998, 0.0)]
     
    _circle_arrow_20_cvs = [(0.0, 1.4824212969595894, 0.0),
     (0.0, 0.9510567784309385, -0.3090170621871948),
     (0.0, 0.8090172410011289, -0.5877854228019714),
     (0.0, 0.587785482406616, -0.8090173006057739),
     (0.0, 0.30901715159416177, -0.951056957244873),
     (0.0, -2.220446049250313e-16, -1.0000004768371582),
     (0.0, -0.3090171515941622, -0.9510570168495178),
     (0.0, -0.587785601615906, -0.8090174794197083),
     (0.0, -0.8090175390243532, -0.5877856016159058),
     (0.0, -0.9510571360588076, -0.3090171813964844),
     (0.0, -1.0000000000000002, 0.0),
     (0.0, -0.9510565400123598, 0.30901700258255005),
     (0.0, -0.8090170025825503, 0.5877853035926819),
     (0.0, -0.5877852439880373, 0.8090170621871948),
     (0.0, -0.3090169727802279, 0.9510565996170044),
     (0.0, 2.9802322165650708e-08, 1.0000001192092896),
     (0.0, 0.3090170621871946, 0.9510566592216492),
     (0.0, 0.5877853631973264, 0.8090171217918396),
     (0.0, 0.8090171813964842, 0.5877853631973267),
     (0.0, 0.9510567784309385, 0.3090170621871948),
     (0.0, 1.4824212969595894, 0.0)]
     
    
    @staticmethod
    def cv_pos_from_crv():
        
        sel_list = pm.ls(sl=True)
        
        if not sel_list:
            pm.warning('Nothing is selected')
            return
        
        if isinstance(sel_list[0], pm.nodetypes.Transform):
            
            try:
                shape = sel_list[0].getShape()
                
            except AttributeError as e:
                pm.warning('Please select a nurbs curve', e)
                return
                
            if not isinstance(shape, pm.nodetypes.NurbsCurve):
                pm.warning('Please select a nurbs curve')
                return
    
        elif isinstance(sel_list[0], pm.nodetypes.NurbsCurve):
            shape =  sel_list[0]   
             
        else:
            pm.warning('Please select a nurbs curve')
            return
    
        
        cv_pos = shape.getCVs()
        
        ret = []
        for p in cv_pos:
            ret.append((p.x, p.y, p.z))
            
        pprint.pprint(ret)
        return ret


    @staticmethod   
    def _build_ctrl(name, pos_list, size=1):
        size_pos = [(p[0]*size, p[1]*size, p[2]*size) for p in pos_list]
        return pm.curve(degree=1, p=size_pos, name=name)

    @staticmethod 
    def create_circle_arrow(name, size):
        CreateCtrl._build_ctrl(name=name, pos_list=CreateCtrl._circle_arrow_20_cvs, size=size)

    @staticmethod 
    def create_circle(name, size):
        CreateCtrl._build_ctrl(name=name, pos_list=CreateCtrl._circle_20_cvs, size=size)

#CreateCtrl.cv_pos_from_crv()
#CreateCtrl.create_circle(name='circle_ctrl', size=1)
#CreateCtrl.create_circle_arrow(name='circle_arrow_ctrl', size=1.2)

'''
import petfactory.rigging.ctrl.ctrl as pet_ctrl
reload(pet_ctrl)
pet_ctrl.CreateCtrl.create_circle_arrow(name='apa', size=12) 
'''




