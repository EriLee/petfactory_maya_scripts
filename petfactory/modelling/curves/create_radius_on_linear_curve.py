import pymel.core as pm
import math, pprint

def line(pos_list, name=''):
    return pm.curve(degree=1, p=pos_list, name=name)
    
def pos(x, y, z=0, name='pos'):
    sp = pm.polySphere(r=.06, name=name)[0]
    sp.translate.set((x, y, z))
    return sp
    
def create_round_corner(pos_list, radius):
    
    # the position return list
    ret_pos_list = []
    
    # define the vectors
    ba_vec = pos_list[0] - pos_list[1]
    bc_vec = pos_list[2] - pos_list[1]
    
    # normalize
    aim_vec = ba_vec.normal()
    up_vec = bc_vec.normal()
    
    # get the cross product of aim and up
    cross_vec = ba_vec.cross(bc_vec).normal()
    
    # make sure the up vector is orthogonal
    up_vec_ortho = cross_vec.cross(aim_vec)
    
    # "project" the vector on the ortogonal vectors using the dot product
    # i.e. find out how much the vector points in the same direction as the
    # orthogonal vector
    aim_u = aim_vec.dot(aim_vec)
    aim_v = aim_vec.dot(up_vec_ortho)
    
    up_u = up_vec.dot(aim_vec)
    up_v = up_vec.dot(up_vec_ortho)
    
    # create pymel vectors
    aim_uv_vec = pm.datatypes.Vector(aim_u, aim_v, 0)
    up_uv_vec = pm.datatypes.Vector(up_u, up_v, 0)

    # cretae the mid vector
    mid_vec = (aim_uv_vec + up_uv_vec).normal()
    
    # visulaize the local vectors
    #line([(0,0,0), aim_uv_vec])
    #line([(0,0,0), up_uv_vec])
    #line([(0,0,0), mid_vec])

    # build a transformation matrix to transform vectors 
    # from world space to the rotated space
    tm = pm.datatypes.TransformationMatrix(
    [aim_vec[0],aim_vec[1],aim_vec[2],0],
    [up_vec_ortho[0], up_vec_ortho[1], up_vec_ortho[2],0],
    [cross_vec[0], cross_vec[1], cross_vec[2], 0],
    #[0,0,0,1])
    [pos_list[1][0],pos_list[1][1],pos_list[1][2],1])
      
    # calculate the theta angle, remember atan2(y, x) or (v, u)
    theta = math.atan2(mid_vec.y, mid_vec.x)  
    #print(theta)
    
    # get the length of the hypotenuse    
    h = radius / math.sin(theta)
    # get the length of the adjacent 
    a = radius / math.tan(theta)
          
    # the angle we need to rotate from positive x axis to the theta angle
    ang = math.pi + theta

    # the angle between theta and the oposite side of the right triangle (1.5 PI)
    # the opposite side are perpendicular to the adjacent side that intersects the circle
    diff_ang = math.pi*1.5 - ang
    
    # number of point we want on the circle perimeter (will be reflected across the mid vector)
    # needs to be at least 2
    num_points = 5
    
    ang_inc = diff_ang/(num_points-1)
    mid_vec_scaled = mid_vec*h
    
    # gather pooint on the circle perimeter
    pos_on_circ = []
    for i in range(num_points):

        rot = ang + ang_inc * (i)
        x = (math.cos(rot)*radius) + (mid_vec_scaled).x
        y = (math.sin(rot)*radius) + (mid_vec_scaled).y
     
        p = pm.datatypes.Vector(x,y,0)
        pos_on_circ.append(p)
        

    # copy and reflect the positions on the circle to get the positions on the circle reflected by the mid vector
    pos_on_circ_reflected = []
    for i in range(1, num_points):

        # reflect around the mid vec
        pos_on_circ_reflected.append(2 * pos_on_circ[i].dot(mid_vec) / mid_vec.dot(mid_vec) * mid_vec - pos_on_circ[i])
 
    # reverse the first pos on circle
    pos_on_circ.reverse()
    
    # merge the pos lists
    ret_pos_list = pos_on_circ[:]
    ret_pos_list += pos_on_circ_reflected 
 

    #for p in ret_pos_list:
    #    pos(p.x, p.y, p.z)
        
    # transform the position to world space  
    for i, p in enumerate(ret_pos_list):
        ret_pos_list[i] = p.rotateBy(tm) + pos_list[1]
        
    for p in ret_pos_list:
        pos(p.x, p.y, p.z)
        

    #---------------------
    
    # visualize:
        
    # get the circle cenyter position
    circ_center = (mid_vec*h).rotateBy(tm)
    circ_center_tm = circ_center
 
    # get the positions where the circle touches the lines
    adjacent_aim = aim_uv_vec.normal() * a
    adjacent_aim_refl = 2 * adjacent_aim.dot(mid_vec) / mid_vec.dot(mid_vec) * mid_vec - adjacent_aim

    # visulaize the local vectors
    adjacent_aim_tm = adjacent_aim.rotateBy(tm) + pos_list[1]
    adjacent_aim_refl_tm = adjacent_aim_refl.rotateBy(tm) + pos_list[1]
    
    
    circ = pm.circle(r=radius, normal=(0,0,1))[0]
    circ.setMatrix(tm)
    circ.translate.set(pos_list[1]+circ_center_tm)
    
    line([pos_list[1]+circ_center_tm, adjacent_aim_tm])
    line([pos_list[1]+circ_center_tm, adjacent_aim_refl_tm])
    line([pos_list[1], pos_list[1]+circ_center_tm])

    #---------------------
    
             
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




