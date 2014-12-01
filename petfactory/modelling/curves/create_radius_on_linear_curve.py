import pymel.core as pm
import math, pprint

def line(pos_list, name=''):
    return pm.curve(degree=1, p=pos_list, name=name)
    
def pos(x, y, z=0):
    sp = pm.polySphere(r=.3)[0]
    sp.translate.set((x, y, z))
    return sp
    
def create_round_corner(pos_list, radius):
    
    ret_pos_list = []
    
    # define the vectors
    ba_vec = pos_list[0] - pos_list[1]
    bc_vec = pos_list[2] - pos_list[1]
    
    # normalize
    aim_vec = ba_vec.normal()
    up_vec = bc_vec.normal()
    
    # get the cross
    abc_cross = ba_vec.cross(bc_vec).normal()
    
    # make sure the up vector is orthogonal
    up_vec_ortho = abc_cross.cross(aim_vec)
    
    # visualize the ortho vectors
    #o = (0,0,0)
    #line([o, aim_vec])
    #line([o, up_vec_ortho])
    
    # "project" the vector on the ortogonal vectors using the dot product
    # i.e. find out how much the vector points in the same direction as the
    # orthogonal vector
    aim_u = aim_vec.dot(aim_vec)
    aim_v = aim_vec.dot(up_vec_ortho)
    
    up_u = up_vec.dot(aim_vec)
    up_v = up_vec.dot(up_vec_ortho)
    
    aim_uv_vec = pm.datatypes.Vector(aim_u, aim_v, 0)
    up_uv_vec = pm.datatypes.Vector(up_u, up_v, 0)
    
    # calculate the mid vector
    mid_u = aim_u + up_u
    mid_v = aim_v + up_v
    mag = math.sqrt(mid_u*mid_u + mid_v*mid_v)
    mid_u_n = mid_u/mag
    mid_v_n = mid_v/mag
    # create a pymel vector
    mid_vec = pm.datatypes.Vector(mid_u_n, mid_v_n, 0) 
    
    
    #build a transformation matrix to transform vectors 
    # from world space to the rotated space
    tm = pm.datatypes.TransformationMatrix(
    [aim_vec[0],aim_vec[1],aim_vec[2],0],
    [up_vec_ortho[0], up_vec_ortho[1], up_vec_ortho[2],0],
    [abc_cross[0], abc_cross[1], abc_cross[2], 0],
    [0,0,0,1])
    
    
    # calculate the theta angle
    theta_ba = math.atan2(aim_v, aim_u)   # aim
    theta_bc = math.atan2(up_v, up_u)     # up
    
    if theta_ba < theta_bc:
        theta_rad = (theta_bc - theta_ba)/2
    else:
        theta_rad = (theta_ba - theta_bc)/2
    
    # get the length of the hypotenuse    
    h = radius / math.sin(theta_rad)
    # get the length of the adjacent 
    a = radius / math.tan(theta_rad)
    
    circle_center = pos_list[1] + (mid_vec*h).rotateBy(tm)
    #pos(circle_center.x, circle_center.y, circle_center.z)
    

    
    ##########################################
    #                                        #
    #    Visualize the world space vectors   # 
    #                                        #
    ##########################################
    
    
    # visualize the vectors oriented to world space
    #o = (0,0,0)
    #line([o, aim_uv_vec*5])
    #line([o, up_uv_vec*5])
    #line([o, mid_vec*5])
    # the circle center pos
    #pos((mid_vec*h).x, (mid_vec*h).y)
    
    

    ##########################################
    #                                        #
    #    positions on the circle perimeter   #
    #                                        #
    ##########################################
    
    
    # the angle we need to rotate from positive x axis to the theta angle
    ang = math.pi + theta_rad

    # the angle between theta and the oposite side of the right triangle (1.5 PI)
    # the opposite side are perpendicular to the adjacent side that intersects the circle
    diff_ang = math.pi*1.5 - ang
    
    # number of point we want on the circle perimeter (will be reflected across the mid vector)
    num_points = 5
    ang_inc = diff_ang/(num_points+1)
    mid_vec_scaled = mid_vec*h
    
    pos_on_circ = []
    pos_on_circ_reflect = []
    for i in range(num_points):

        rot = ang + ang_inc * (i+1)
        
        x = (math.cos(rot)*radius) + (mid_vec_scaled).x
        y = (math.sin(rot)*radius) + (mid_vec_scaled).y
     
        p = pm.datatypes.Vector(x,y,0)
        p_tm = p.rotateBy(tm) + pos_list[1]
        # visualize
        #pos(p_tm.x, p_tm.y, p_tm.z)
        pos_on_circ.append(p_tm)
        
        # reflect around the mid vec
        p_refl = 2 * p.dot(mid_vec_scaled) / mid_vec_scaled.dot(mid_vec_scaled) * mid_vec_scaled - p   
        p_refl_tm = p_refl.rotateBy(tm) + pos_list[1] 
        #pos(p_refl_tm.x, p_refl_tm.y, p_refl_tm.z)
        pos_on_circ_reflect.append(p_refl_tm)
        
        # visualize the pos along circle perimeter
        #pos(p.x, p.y, p.z)
        #pos(p_refl.x, p_refl.y, p_refl.z)
        
    
    
    #h_vec = pm.datatypes.Vector(h, 0, 0)
    #h_vec_tm = pos_list[1] + h_vec.rotateBy(tm)
    #pos(h_vec_tm.x, h_vec_tm.y, h_vec_tm.z)
        
    # get the positions where the circle touches the lines
    adjacent_aim = (aim_uv_vec.normal() * a).rotateBy(tm) + pos_list[1]
    #pos(adjacent_aim.x, adjacent_aim.y, adjacent_aim.z)
    
    # could also reflect to get this position
    adjacent_up = (up_uv_vec.normal() * a).rotateBy(tm) + pos_list[1]
    #pos(adjacent_up.x, adjacent_up.y, adjacent_up.z)
    
    
    # get the circle cenyter position
    circ_center = (mid_vec*h).rotateBy(tm)
    circ_center_tm = circ_center
    
    #circ = pm.circle(r=radius, normal=(0,0,1))[0]
    #circ.setMatrix(tm)
    #circ.translate.set(pos_list[1]+circ_center_tm)
    
    # the position where the mid line first intersects the circle
    mid_pos_on_circ = mid_vec*(h-radius)
    mid_pos_on_circ_tm = mid_pos_on_circ.rotateBy(tm)+pos_list[1]
    
    
    #pos(mid_pos_on_circ_tm.x, mid_pos_on_circ_tm.y, mid_pos_on_circ_tm.z)
    
    #line([pos_list[1], pos_list[1]+circ_center])
    #line([adjacent_aim, pos_list[1]+circ_center])
    #line([adjacent_up, pos_list[1]+circ_center])
    
    # reverse the list of positions on the curves
    pos_on_circ.reverse()
    
    ret_pos_list.append(adjacent_aim)
    ret_pos_list += pos_on_circ
    ret_pos_list.append(mid_pos_on_circ_tm)
    ret_pos_list += pos_on_circ_reflect
    ret_pos_list.append(adjacent_up)
    
    return ret_pos_list
    
    
# delete all
'''
sel_all = pm.ls(type='transform')
for x in sel_all:
    if x.name() != 'crv':
        pm.delete(x)  
'''


def add_smooth_corners(radius=1, radius_list=None):
    
    sel_list = pm.ls(sl=True)
        
    if not sel_list:
        pm.warning('Please select a NurbsCurve transform')
        return
    
    if not isinstance(sel_list[0], pm.nodetypes.Transform):
        pm.warning('Please select a NurbsCurve transform')
        return
    
    try:
        crv = sel_list[0].getShape()
        
    except:
        pm.warning('Please select a NurbsCurve transform')
        return
    

    # get the cv positions
    cv_pos_list = crv.getCVs(space='world')  
    num_cvs = len(cv_pos_list)
    
    # if we have aradius list specified
    if radius_list is not None:
        
        if num_cvs-2 != len(radius_list):
            pm.warning('The length of the radius list {0} do not match the number of corners {1}'.format(len(radius_list), num_cvs-2))
        

    crv_build_cv_list = []
    
    
    for index in range(num_cvs):
        
        if index is 0:
            crv_build_cv_list.append(cv_pos_list[0])
            
        elif index is num_cvs-1:
            crv_build_cv_list.append(cv_pos_list[-1])
            
        else:
            
            if radius_list is not None:
                radius = radius_list[index-1]
                
            p_list = cv_pos_list[index-1:index+2] 
            p = create_round_corner(p_list, radius)
            crv_build_cv_list += p
    
        
    pm.curve(d=1, p=crv_build_cv_list)


        
#add_smooth_corners(radius=1)
add_smooth_corners(radius_list=[5,4,3,2,1,.5])




