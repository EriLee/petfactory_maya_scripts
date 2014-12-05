import pymel.core as pm
import pprint

loc_o = pm.PyNode('locator1')
loc_t = pm.PyNode('locator2')

world_m = loc_t.getMatrix()
world_tm = pm.datatypes.TransformationMatrix(world_m)


#loc_om = loc_o.getMatrix()
#x = loc_om[0][0]
#y = loc_om[0][1]

lp = loc_o.getTranslation(s='world')
x = lp.x
y = lp.y

for z in range(10):
    
    local_vector = pm.datatypes.Vector(x, y, z)
    print(local_vector)
    
    vector_in_world = local_vector.rotateBy(world_tm)

    z_wp = vector_in_world + world_tm.getTranslation(space='world')
    
    sl = pm.spaceLocator()
    sl.translate.set(z_wp)



'''
random note on 2d rotation....


2D rotation

clockwise about the origin

functional form:

x' =  x * cos(theta) + y * sin(theta)
y' = -x * sin(theta) + y * cos(theta)

matrix form:

x' = | cos(theta)  sin(theta) |   | x |
     |                        | x |   |
y' = | cos(theta)  sin(theta) |   | y |


'''
        


