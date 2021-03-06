from wisdem.floating.turbine_spar_instance import TurbineSparInstance
from floatingse.instance.tlp_instance import TLPInstance
import numpy as np
import offshorebos.wind_obos as wind_obos
from baselineSpar import mypromote, setobj
from shutil import copyfile, move


def mysetup(myobj, discrete=True):

    myobj.add_design_variable('fairlead_location',0.0, 1.0)
    myobj.add_design_variable('fairlead_offset_from_shell',5.0, 30.0)
    myobj.add_design_variable('fairlead_support_wall_thickness',1e-3, 1.0)
    myobj.add_design_variable('fairlead_support_outer_diameter',1e-1, 10.0)
    myobj.add_design_variable('main_freeboard',0.0, 50.0)
    myobj.add_design_variable('main_section_height',1e-1, 50.0)
    myobj.add_design_variable('main_outer_diameter',2.1, 20.0)
    myobj.add_design_variable('main_wall_thickness',1e-3, 5e-1)
    myobj.add_design_variable('main_buoyancy_tank_diameter',0.0, 50.0)
    myobj.add_design_variable('main_buoyancy_tank_height',0.0, 20.0)
    myobj.add_design_variable('main_buoyancy_tank_location',0.0, 1.0)
    myobj.add_design_variable('tower_section_height',1e-1, 100.0)
    myobj.add_design_variable('tower_outer_diameter',1.1, 20.0)
    myobj.add_design_variable('tower_wall_thickness',1e-3, 5e-1)
    myobj.add_design_variable('mooring_line_length', 10.0, 300.0)
    myobj.add_design_variable('anchor_radius', 20.0, 1e2)
    myobj.add_design_variable('mooring_diameter', 0.05, 5.0)
    myobj.add_design_variable('main_permanent_ballast_height', 1e-1, 50.0)
    myobj.add_design_variable('main_stiffener_web_height', 1e-2, 1.0)
    myobj.add_design_variable('main_stiffener_web_thickness', 1e-3, 5e-1)
    myobj.add_design_variable('main_stiffener_flange_width', 1e-2, 5.0)
    myobj.add_design_variable('main_stiffener_flange_thickness', 1e-3, 5e-1)
    myobj.add_design_variable('main_stiffener_spacing', 1e-1, 1e2)
    if discrete:
        myobj.add_design_variable('number_of_mooring_connections', 3, 4)
        myobj.add_design_variable('mooring_lines_per_connection', 1, 3)
    
    for c in myobj.get_constraints():
        if c[0].find('modal') >= 0: continue
        #elif c[0].find('tip') >= 0: continue
        #elif c[0].find('period') >= 0: continue
        #elif c[0].find('heel_moment') >= 0: continue
        #elif c[0].find('axial_unity') >= 0: continue
        #elif ((c[0].find('tow.') >= 0) and (c[0].find('height') < 0)): continue
        #elif c[0].find('metacentric') >= 0: continue
        elif c[0].find('freeboard_heel') >= 0: continue
        elif c[0].find('off') >= 0: continue
        #elif c[0].find('pontoon_stress') >= 0: continue

        myobj.add_constraint(c[0], c[1], c[2], c[3])

    return setobj(myobj)

subsave    = 'tlp-v0.save'
turbsave   = 'turb-tlp-v0.save'

mysub = TLPInstance()
mysub.set_reference('10MW')
mysub.params['water_depth'] = 320.0
mysub.params['Hs'] = 10.8
mysub.params['T'] = 9.8
mysub.params['Uref'] = 11.0
mysub.params['zref'] = 119.0
mysub.params['max_offset'] = 100.0
mysub.params['mooring_type'] = 'nylon'
mysub.params['number_of_offset_columns'] = 0
mysub.params['max_draft'] = 35.0

myturb = TurbineSparInstance('10MW')
myturb.set_reference('10MW')
myturb.params['water_depth'] = 320.0
myturb.params['wave_height'] = 10.8
myturb.params['wave_period'] = 9.8
myturb.params['wind_reference_speed'] = 11.0
myturb.params['wind_reference_height'] = 119.0
myturb.params['mooring_type'] = 'nylon'
myturb.params['anchor'] = wind_obos.Anchor.SUCTIONPILE
myturb.params['number_of_offset_columns'] = 0


if __name__ == '__main__':

    mysub.load(subsave)

    # SOGA (global)
    mysub.set_optimizer('soga')
    mysub.set_options({'generations':4000,
                       'population':40,
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
                       'penalty_multiplier':1e5})
    mysub = mysetup(mysub, False)
    mysub.run()
    mysub.save(subsave)
    move('heuristic.restart','nm.restart')

    # NM (fine)
    mysub.load(subsave)
    mysub.set_optimizer('nm')
    mysub.set_options({'generations':6000,
                       'nstall':1000,
                       'penalty':True,
                       'restart':False,
                       'tol':1e-6,
                       'global_search':False,
                       'adaptive_simplex':True,
                       'penalty_multiplier':1e5})
    mysub = mysetup(mysub, False)
    mysub.run()
    mysub.save(subsave)
    move('heuristic.restart','nm.restart')

    # Subplex (again)
    mysub.load(subsave)
    mysub.set_optimizer('subplex')
    mysub.set_options({'generations':100,
                       'nstall':20,
                       'penalty':True,
                       'restart':False,
                       'tol':1e-6,
                       'global_search':False,
                       'adaptive_simplex':False,
                       'penalty_multiplier':1e5})
    mysub = mysetup(mysub, False)
    mysub.run()
    mysub.save(subsave)
    move('heuristic.restart','subplex.restart')

    mysub.load(subsave)
    mypromote(mysub, myturb)
    myturb.save(turbsave)
