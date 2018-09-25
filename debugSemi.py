from wisdem.floating.turbine_semi_instance import TurbineSemiInstance
from floatingse.instance.semi_instance import SemiInstance
import numpy as np
from baselineSemi import mysetup



subsave    = 'semi-soga.save'
turbsave   = 'turb-semi-soga.save'
optstr     = 'nm'
subsaveopt = subsave.replace('soga',optstr)

mysub = SemiInstance()
mysub.set_reference('10MW')
mysub.params['water_depth'] = 320.0
mysub.params['Hs'] = 10.8
mysub.params['T'] = 9.8
mysub.params['Uref'] = 11.0
mysub.params['zref'] = 119.0
mysub.params['mooring_max_offset'] = 100.0

myturb = TurbineSemiInstance('10MW')
myturb.set_reference('10MW')
myturb.params['water_depth'] = 320.0
myturb.params['wave_height'] = 10.8
myturb.params['wave_period'] = 9.8
myturb.params['wind_reference_speed'] = 11.0
myturb.params['wind_reference_height'] = 119.0

myturb2 = TurbineSemiInstance('10MW')

if __name__ == '__main__':

    # SOGA
    mysub.load(subsave)
    mysub.set_optimizer('nm')
    mysub.set_options({'generations':1, 'nstall':1000, 'penalty':True, 'restart':True, 'adaptive_simplex':True, 'tol':1e-6, 'global_search':False})
    mysub = mysetup(mysub, False)
    mysub.run()
    mysub.save(subsave)

    
