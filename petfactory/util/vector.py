import pymel.core as pm

def interpolate_positions(pos_list, num_divisions=1):
    
    u_inc = 1.0 / (num_divisions+1)
    last_index = len(pos_list)-1
    
    ret_pos_list = []
    for index, pos in enumerate(pos_list):
        
        if index < last_index:
            
            dx = pos_list[index+1][0] - pos_list[index][0]
            dy = pos_list[index+1][1] - pos_list[index][1]
            dz = pos_list[index+1][2] - pos_list[index][2]
            
            for u in range(num_divisions+1):
                ret_pos_list.append((   pos_list[index][0] + dx*u*u_inc,
                                        pos_list[index][1] + dy*u*u_inc,
                                        pos_list[index][2] + dz*u*u_inc))
    
        else:
            ret_pos_list.append(pos_list[-1])
    
    return ret_pos_list

def viz_vec_3(end, start=(0,0,0), name='curve', color_index=16):
                   
    pos = ([end[0], end[1], end[2]], [start[0], start[1], start[2]])        
    crv = pm.curve(degree=1, p=pos, name=name)   
    
    # 6:blue, 16:white, 17:yellow
    if(color_index):
        pm.setAttr('{0}.overrideEnabled'.format(crv.getShape()), 1)
        pm.setAttr('{0}.overrideColor'.format(crv.getShape()), color_index)
        
    return [crv, crv.getShape()]
    

def viz_sphere(pos, name='sphere', color_index=16):
                          
    sphere = pm.sphere(p=pos, name=name, radius=.1)[0]
    
    # 6:blue, 16:white, 17:yellow
    if(color_index):
        print(1231413541345)
        pm.setAttr('{0}.overrideEnabled'.format(sphere.getShape()), 1)
        pm.setAttr('{0}.overrideColor'.format(sphere.getShape()), color_index)
        
    return sphere
         
def ortho_aim_up(aim_vec, up_vec, invert_aim=False, invert_up=False):
    '''returns a dict with orthogonal vectors for aim, up and cross'''

    if aim_vec == up_vec:
        pm.warning('The joint aim vector can not be equal to the joint up vector!')
        return None
            
    # create a pymel vector and normalize
    aim_vec = pm.datatypes.Vector(aim_vec[0], aim_vec[1], aim_vec[2])
    up_vec = pm.datatypes.Vector(up_vec[0], up_vec[1], up_vec[2])
      
    # normalize the input vectors
    vec_aim_n = aim_vec.normal()
    vec_up_n = up_vec.normal()
    
    # invert the vectors 
    if invert_aim:
        vec_aim_n *= -1
            
    if invert_up:
        vec_up_n *= -1
        
    # get the cross product 
    vec_cross = vec_up_n.cross(vec_aim_n)
    
    # make sure that the up vector is orthogonal
    vec_up_orto_n = vec_aim_n.cross(vec_cross)
    
    return {'aim':vec_aim_n , 'up':vec_up_orto_n, 'cross':vec_cross}
        
def remap_aim_up(aim_vec, up_vec, aim_axis=0, up_axis=2, invert_aim=False, invert_up=False, pos=(0,0,0)):
    '''remaps the aim and up vectors to any vector specified.
    Returns a pymel transformation matrix'''
    
    if aim_axis == up_axis:
        pm.warning('The joint aim axis can not be equal to the joint up axis!')
        return
        
    # get orthogonal axis
    ortho_axis = ortho_aim_up(aim_vec=aim_vec, up_vec=up_vec, invert_aim=invert_aim, invert_up=invert_up)
    
    if not ortho_axis:
    	return None
    # the position
    pos = pm.datatypes.Vector(pos[0], pos[1], pos[2])
    
    vx = False
    vy = False
    vz = False

    # aim vector ---------------
    
    # x aim
    if aim_axis is 0:
        vx = ortho_axis.get('aim')
        
    # y aim
    elif aim_axis is 1:
        vy = ortho_axis.get('aim')
            
    # z aim
    else:
        vz = ortho_axis.get('aim')
            
            
    # up vector ---------------
          
    # x up
    if up_axis is 0:
        vx = ortho_axis.get('up')
        
    # y up
    elif up_axis is 1:
        vy = ortho_axis.get('up')
            
    # z up
    else:
        vz = ortho_axis.get('up')
        
        
    # cross vector ---------------
    
    if not vx:
        vx = vy.cross(vz)
        
    if not vy:
        vy = vz.cross(vx)
        
    if not vz:
        vz = vx.cross(vy)
                
     
    return pm.datatypes.TransformationMatrix([vx, vy, vz, pos])
    
    
def rot_vec_pos(transform):
    '''returns the normalized rotation vectors and position of the specified transform.
    Returns a dict with x,y,z and rot as key, pymel vectors a value.
    '''
    
    if not isinstance(transform, pm.nodetypes.Transform):
        pm.warning('requires a transform')
        return
        
    matrix = transform.getMatrix(ws=True)
    
    x = pm.datatypes.Vector(matrix[0][0], matrix[0][1], matrix[0][2]).normal()
    y = pm.datatypes.Vector(matrix[1][0], matrix[1][1], matrix[1][2]).normal()
    z = pm.datatypes.Vector(matrix[2][0], matrix[2][1], matrix[2][2]).normal()
    pos = pm.datatypes.Vector(matrix[3][0], matrix[3][1], matrix[3][2])
    
    return {'x':x, 'y':y, 'z':z, 'pos':pos}
    
'''   
d = [n for n in pm.ls(type='transform') if isinstance(n.getShape(), pm.nodetypes.NurbsCurve)]
pm.delete(d)

s = [n for n in pm.ls(type='transform') if isinstance(n.getShape(), pm.nodetypes.NurbsSurface)]
pm.delete(s)

   
import petfactory.util.vector as u_vec


cube = pm.PyNode('pCube1')
cube2 = pm.PyNode('pCube2')
vd = u_vec.rot_vec_pos(cube)

aim = vd.get('z')
up = vd.get('x')
pos = vd.get('pos')

tm = u_vec.remap_aim_up(aim_vec=aim, up_vec=up, aim_axis=2, up_axis=0, pos=pos)

# values: 'transform', 'preTransform', 'object', 'world'
tm.addTranslation((2,2,0), 'preTransform')
cube2.setMatrix(tm)

'''

