import pymel.core as pm

sel_list = pm.ls(sl=True)


scale_factor = .75

a_crv = sel_list[0].getShape()
b_crv = sel_list[1].getShape()


a_crv_num_cv = a_crv.numCVs()
a_crv_cv_list = a_crv.getCVs()
a_crv_pos_end = a_crv_cv_list[-1]


b_crv_num_cv = b_crv.numCVs()
b_crv_cv_list = b_crv.getCVs()
b_crv_pos_start = b_crv_cv_list[0]

a_extend_pos_norm = ((a_crv_cv_list[-1] - a_crv_cv_list[-2]).normal())*scale_factor + a_crv_cv_list[-1]
b_extend_pos_norm = ((b_crv_cv_list[0] - b_crv_cv_list[1]).normal())*scale_factor + b_crv_cv_list[0]


loc_a = pm.spaceLocator()
loc_a.translate.set(a_extend_pos_norm)

loc_b = pm.spaceLocator()
loc_b.translate.set(b_extend_pos_norm)


pos_list = (    [a_crv_pos_end[0], a_crv_pos_end[1], a_crv_pos_end[2]],
                [a_extend_pos_norm[0], a_extend_pos_norm[1], a_extend_pos_norm[2]],
                [b_extend_pos_norm[0], b_extend_pos_norm[1], b_extend_pos_norm[2]],
                [b_crv_pos_start[0], b_crv_pos_start[1], b_crv_pos_start[2]],
)
pm.curve(degree=3, p=pos_list, name='name')