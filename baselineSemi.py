from wisdem.floating.turbine_semi_instance import TurbineSemiInstance
from floatingse.instance.semi_instance import SemiInstance
import numpy as np
from baselineSpar import mypromote, setobj
from shutil import copyfile, move

def mysetup(myobj, discrete=True):

    myobj.add_design_variable('fairlead_location',0.0, 1.0)
    myobj.add_design_variable('fairlead_offset_from_shell',0.0, 5.0)
    myobj.add_design_variable('fairlead_support_wall_thickness',1e-3, 1.0)
    myobj.add_design_variable('fairlead_support_outer_diameter',1e-1, 10.0)
    myobj.add_design_variable('main_freeboard',0.0, 50.0)
    myobj.add_design_variable('main_section_height',1e-1, 50.0)
    myobj.add_design_variable('main_outer_diameter',2.1, 40.0)
    myobj.add_design_variable('main_wall_thickness',1e-3, 5e-1)
    myobj.add_design_variable('main_buoyancy_tank_diameter',0.0, 50.0)
    myobj.add_design_variable('main_buoyancy_tank_height',0.0, 20.0)
    myobj.add_design_variable('main_buoyancy_tank_location',0.0, 1.0)
    myobj.add_design_variable('offset_freeboard',2.0, 15.0)
    myobj.add_design_variable('offset_section_height',1e-1, 50.0)
    myobj.add_design_variable('offset_outer_diameter',1.1, 40.0)
    myobj.add_design_variable('offset_wall_thickness',1e-3, 5e-1)
    myobj.add_design_variable('offset_buoyancy_tank_diameter',0.0, 50.0)
    myobj.add_design_variable('offset_buoyancy_tank_height',0.0, 20.0)
    myobj.add_design_variable('offset_buoyancy_tank_location',0.0, 1.0)
    myobj.add_design_variable('pontoon_outer_diameter', 1.0, 10.0)
    myobj.add_design_variable('pontoon_wall_thickness', 1e-2, 1.0)
    myobj.add_design_variable('main_pontoon_attach_lower',0.0, 0.5)
    myobj.add_design_variable('main_pontoon_attach_upper',0.5, 1.0)
    myobj.add_design_variable('tower_section_height',1e-1, 100.0)
    myobj.add_design_variable('tower_outer_diameter',1.1, 20.0)
    myobj.add_design_variable('tower_wall_thickness',1e-3, 5e-1)
    myobj.add_design_variable('mooring_line_length', 2e2, 3e3)
    myobj.add_design_variable('anchor_radius', 1e2, 5e3)
    myobj.add_design_variable('mooring_diameter', 0.05, 2.0)
    myobj.add_design_variable('main_permanent_ballast_height', 1e-1, 50.0)
    myobj.add_design_variable('main_stiffener_web_height', 1e-2, 1.0)
    myobj.add_design_variable('main_stiffener_web_thickness', 1e-3, 5e-1)
    myobj.add_design_variable('main_stiffener_flange_width', 1e-2, 5.0)
    myobj.add_design_variable('main_stiffener_flange_thickness', 1e-3, 5e-1)
    myobj.add_design_variable('main_stiffener_spacing', 1e-1, 1e2)
    myobj.add_design_variable('offset_stiffener_web_height', 1e-2, 1.0)
    myobj.add_design_variable('offset_stiffener_web_thickness', 1e-3, 5e-1)
    myobj.add_design_variable('offset_stiffener_flange_width', 1e-2, 5.0)
    myobj.add_design_variable('offset_stiffener_flange_thickness', 1e-3, 5e-1)
    myobj.add_design_variable('offset_stiffener_spacing', 1e-1, 1e2)
    myobj.add_design_variable('offset_permanent_ballast_height', 1e-1, 50.0)
    myobj.add_design_variable('radius_to_offset_column', 5.0, 100.0)
    if discrete:
        #myobj.add_design_variable('number_of_mooring_connections', 3, 4)
        myobj.add_design_variable('mooring_lines_per_connection', 1, 3)
        #myobj.add_design_variable('number_of_offset_columns', 3, 4)
        myobj.add_design_variable('outer_cross_pontoons_int', 0, 1)
        myobj.add_design_variable('cross_attachment_pontoons_int', 0, 1)
        myobj.add_design_variable('lower_attachment_pontoons_int', 0, 1)
        myobj.add_design_variable('upper_attachment_pontoons_int', 0, 1)
        myobj.add_design_variable('lower_ring_pontoons_int', 0, 1)
        myobj.add_design_variable('upper_ring_pontoons_int', 0, 1)

    for c in myobj.get_constraints():
        if c[0].find('modal') >= 0: continue
        #elif c[0].find('tip') >= 0: continue
        #elif c[0].find('period') >= 0: continue
        #elif c[0].find('heel_moment') >= 0: continue
        #elif c[0].find('axial_unity') >= 0: continue
        elif c[0].find('metacentric') >= 0: 
            myobj.add_constraint(c[0], 1e-1, c[2], c[3])
            continue
        #elif ((c[0].find('tow.') >= 0) and (c[0].find('height') < 0)): continue

        myobj.add_constraint(c[0], c[1], c[2], c[3])

    myobj.params['number_of_mooring_connections'] = 3
    myobj.params['number_of_offset_columns'] = 3

    return setobj(myobj)



subsave    = 'semi-soga.save'
turbsave   = 'turb-semi-soga.save'

mysub = SemiInstance()
mysub.set_reference('10MW')
mysub.params['water_depth'] = 320.0
mysub.params['Hs'] = 10.8
mysub.params['T'] = 9.8
mysub.params['Uref'] = 11.0
mysub.params['zref'] = 119.0
mysub.params['max_offset'] = 100.0
mysub.params['max_draft'] = 30.0

myturb = TurbineSemiInstance('10MW')
myturb.set_reference('10MW')
myturb.params['water_depth'] = 320.0
myturb.params['wave_height'] = 10.8
myturb.params['wave_period'] = 9.8
myturb.params['wind_reference_speed'] = 11.0
myturb.params['wind_reference_height'] = 119.0
    
if __name__ == '__main__':

    mysub.load(subsave)

    # SOGA (global)
    mysub.set_optimizer('soga')
    mysub.set_options({'generations':4000,
                       'population':50,
                       'restart':False,
                       'penalty':True,
                       'penalty_multiplier':1e2,
                       'nstall':1000,
                       'probability_of_mutation':0.4})
    mysub = mysetup(mysub)
    mysub.run()
    mysub.save(subsave)
    move('heuristic.restart','soga.restart')

    # Subplex (local)
    mysub.load(subsave)
    mysub.set_optimizer('subplex')
    mysub.set_options({'generations':100,
                       'nstall':20,
                       'penalty':True,
                       'restart':False,
                       'tol':1e-6,
                       'global_search':False,
                       'adaptive_simplex':False,
                       'penalty_multiplier':1e3})
    mysub = mysetup(mysub, False)
    mysub.run()
    mysub.save(subsave)
    move('heuristic.restart','subplex.restart')

    # NM (coarse)
    mysub.load(subsave)
    mysub.set_optimizer('nm')
    mysub.set_options({'generations':2000,
                       'nstall':200,
                       'penalty':True,
                       'restart':False,
                       'tol':1e-6,
                       'global_search':False,
                       'adaptive_simplex':False,
                       'penalty_multiplier':1e3})
    mysub = mysetup(mysub, False)
    mysub.run()
    mysub.save(subsave)
    move('heuristic.restart','nm.restart')

    # NM (fine)
    mysub.load(subsave)
    mysub.set_optimizer('nm')
    mysub.set_options({'generations':5000,
                       'nstall':1000,
                       'penalty':True,
                       'restart':False,
                       'tol':1e-6,
                       'global_search':False,
                       'adaptive_simplex':True,
                       'penalty_multiplier':1e3})
    mysub = mysetup(mysub, False)
    mysub.run()
    mysub.save(subsave)
    move('heuristic.restart','nm.restart')

    mysub.load(subsave)
    mypromote(mysub, myturb)
    myturb.save(turbsave)
