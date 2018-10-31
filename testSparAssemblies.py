from wisdem.floating.turbine_spar_instance import TurbineSparInstance
from wisdem.floating.turbine_semi_instance import TurbineSemiInstance
from floatingse.instance.spar_instance import SparInstance
from baselineSpar import mysetup
import numpy as np

subsave    = 'spar-v0.save'
turbsave   = 'turb-spar-v0.save'


mysub = SparInstance()
mysub.set_reference('10MW')
mysub.params['water_depth'] = 320.0
mysub.params['Hs'] = 10.8
mysub.params['T'] = 9.8
mysub.params['Uref'] = 11.0
mysub.params['zref'] = 119.0
mysub.params['max_offset'] = 100.0
mysub.evaluate()

myturb = TurbineSparInstance('10MW')
myturb.set_reference('10MW')
myturb.params['water_depth'] = 320.0
myturb.params['wave_height'] = 10.8
myturb.params['wave_period'] = 9.8
myturb.params['wind_reference_speed'] = 11.0
myturb.params['wind_reference_height'] = 119.0
myturb.evaluate()

myturb = TurbineSemiInstance('10MW')
myturb.set_reference('10MW')
myturb.params['water_depth'] = 320.0
myturb.params['wave_height'] = 10.8
myturb.params['wave_period'] = 9.8
myturb.params['wind_reference_speed'] = 11.0
myturb.params['wind_reference_height'] = 119.0
myturb.evaluate()

