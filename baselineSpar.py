from wisdem.floating.turbine_spar_instance import TurbineSparInstance
from floatingse.instance.spar_instance import SparInstance
from rotorse import NREL5MW, DTU10MW
import numpy as np

subsave  = 'spar-soga.save'
turbsave = 'turb-spar-soga.save'

myspar = SparInstance()
myspar.set_reference('10MW')
myspar.load(subsave)

# SOGA
myspar.set_optimizer('soga')
myspar.set_options({'generations':5000, 'population':50, 'restart':False, 'penalty':True})
myspar.add_design_variable('fairlead',0.0, 100.0)
myspar.add_design_variable('fairlead_offset_from_shell',0.0, 5.0)
myspar.add_design_variable('fairlead_support_wall_thickness',1e-3, 1e-1)
myspar.add_design_variable('fairlead_support_outer_diameter',1e-2, 5.0)
myspar.add_design_variable('base_freeboard',0.0, 50.0)
myspar.add_design_variable('base_section_height',1e-1, 50.0)
myspar.add_design_variable('base_outer_diameter',2.1, 20.0)
myspar.add_design_variable('base_wall_thickness',1e-3, 5e-1)
myspar.add_design_variable('tower_section_height',1e-1, 100.0)
myspar.add_design_variable('tower_outer_diameter',1.1, 20.0)
myspar.add_design_variable('tower_wall_thickness',1e-3, 5e-1)
myspar.add_design_variable('mooring_line_length', 100.0, 1000.0)
myspar.add_design_variable('anchor_radius', 1.0, 1e3)
myspar.add_design_variable('mooring_diameter', 0.05, 1.0)
myspar.add_design_variable('base_permanent_ballast_height', 1e-1, 50.0)
myspar.add_design_variable('base_stiffener_web_height', 1e-2, 1.0)
myspar.add_design_variable('base_stiffener_web_thickness', 1e-3, 5e-1)
myspar.add_design_variable('base_stiffener_flange_width', 1e-2, 5.0)
myspar.add_design_variable('base_stiffener_flange_thickness', 1e-3, 5e-1)
myspar.add_design_variable('base_stiffener_spacing', 1e-1, 1e2)
myspar.add_design_variable('number_of_mooring_lines', 3, 6)

#myspar.evaluate()
myspar.run()
myspar.save(subsave)
#myspar.visualize()#'spar-soga.jpg')

# Now shift to whole turbine
myturb = TurbineSparInstance(DTU10MW())
myturb.set_reference('10MW')
for k in myturb.params.keys():
    if myspar.params.has_key(k):
        myturb.params[k] = myspar.params[k]

myturb.set_optimizer('soga')
myturb.set_options({'generations':5000, 'population':40, 'restart':False, 'penalty':True})
myturb.add_design_variable('fairlead',0.0, 100.0)
myturb.add_design_variable('fairlead_offset_from_shell',0.0, 5.0)
myturb.add_design_variable('fairlead_support_wall_thickness',1e-3, 1e-1)
myturb.add_design_variable('fairlead_support_outer_diameter',1e-2, 5.0)
myturb.add_design_variable('base_freeboard',0.0, 50.0)
myturb.add_design_variable('base_section_height',1e-1, 50.0)
myturb.add_design_variable('base_outer_diameter',2.1, 20.0)
myturb.add_design_variable('base_wall_thickness',1e-3, 1e-1)
myturb.add_design_variable('tower_section_height',1e-1, 100.0)
myturb.add_design_variable('tower_outer_diameter',1.1, 20.0)
myturb.add_design_variable('tower_wall_thickness',1e-3, 1e-1)
myturb.add_design_variable('mooring_line_length', 100.0, 1000.0)
myturb.add_design_variable('anchor_radius', 1.0, 1e3)
myturb.add_design_variable('mooring_diameter', 0.05, 1.0)
myturb.add_design_variable('base_permanent_ballast_height', 1e-1, 50.0)
myturb.add_design_variable('base_stiffener_web_height', 1e-2, 1.0)
myturb.add_design_variable('base_stiffener_web_thickness', 1e-3, 1e-1)
myturb.add_design_variable('base_stiffener_flange_width', 1e-2, 5.0)
myturb.add_design_variable('base_stiffener_flange_thickness', 1e-3, 1e-1)
myturb.add_design_variable('base_stiffener_spacing', 1e-1, 1e2)
myturb.add_design_variable('number_of_mooring_lines', 3, 6)
myturb.run()
myturb.save(turbsave)
