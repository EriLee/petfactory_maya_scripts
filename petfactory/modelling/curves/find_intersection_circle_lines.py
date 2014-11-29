import pymel.core as pm
import math

def draw_radius(pos_list, radius=1.0, line_length=1):

    # get the vector B - A (second to first cv)
    ba_vec = (pos_list[0] - pos_list[1])
    # get the vector B - C (second to third cv)
    bc_vec = (pos_list[2] - pos_list[1])
    
    # normalize the vectors
    ba_vec_n = ba_vec.normal()
    bc_vec_n = bc_vec.normal()
    
    # calculate the mid vector
    mid_vec_n = (ba_vec_n + bc_vec_n).normal()
    
    # get the angle of the vectors
    theta_ba = math.atan2(ba_vec_n.y, ba_vec_n.x)
    theta_bc = math.atan2(bc_vec_n.y, bc_vec_n.x)
    
    # If the angle of BA is less than angle BC
    # we subbtract angle BA from angle BC
    # we also divide the angle with 2 to get the
    # angle in the "triangle"
    if theta_ba < theta_bc:
        theta_rad = (theta_bc - theta_ba)/2
    else:
        theta_rad = (theta_ba - theta_bc)/2
        
    # find where on the hypotenuse the circle should be drawn
    # i.e. get the length of the hypotenuse in the right triangle
    # using angle theta and the radius (opposite leg)
    h = radius / math.sin(theta_rad)
    #print(h)
    
    # draw the mid line
    line_length = h if not line_length else line_length
    
    line(pos_list[1], pos_list[1]+mid_vec_n*line_length)
    
    # get the circle cenyter position
    circ_center = mid_vec_n*h
    circ = pm.circle(r=radius, normal=(0,0,1))[0]
    circ.translate.set(pos_list[1]+circ_center)
    

# get the curve
crv = pm.PyNode('crv')
# get the cv positions
pos_list = crv.getShape().getCVs(space='world')

num_cv = len(pos_list)
for index, pos in enumerate(pos_list):
    
    if index is not 0 and index < num_cv-1:
        print(pos_list[index+1])
        draw_radius(pos_list[index-1:index+2], radius=.75, line_length=None)
        



