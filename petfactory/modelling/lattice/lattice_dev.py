#lattice = pm.lattice( dv=(2, 2, 2), oc=True)


#pm.select('{0}.pt[4:7]'.format(lattice[1]),r=True)

def move_lattice(lattice, pos_id_dict):
    
    for id, pos in pos_id_dict.iteritems():
        x, y, z = id
        pm.select('{0}.pt[{1}][{2}][{3}]'.format(lattice, x, y, z),r=True)
        pm.move(pos, a=True)
        #print(x, y, x, pos)

        

pos_id_dict = {
    (0,0,0):(-.2,-.3,-.5),
    (0,0,1):(-.2,-.3,.5)

}
move_lattice(lattice[1], pos_id_dict)