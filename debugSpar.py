from wisdem.floating.turbine_spar_instance import TurbineSparInstance
from floatingse.instance.spar_instance import SparInstance
from baselineSpar import mysetup
import numpy as np



subsave    = 'spar-soga.save'
turbsave   = 'turb-spar-soga.save'
optstr     = 'psqp'
subsaveopt = subsave.replace('soga',optstr)

mysub = SparInstance()
mysub.set_reference('10MW')
mysub.params['water_depth'] = 320.0
mysub.params['Hs'] = 10.8
mysub.params['T'] = 9.8
mysub.params['Uref'] = 11.0
mysub.params['zref'] = 119.0
mysub.params['mooring_max_offset'] = 100.0

myturb = TurbineSparInstance('10MW')
myturb.set_reference('10MW')
myturb.params['water_depth'] = 320.0
myturb.params['wave_height'] = 10.8
myturb.params['wave_period'] = 9.8
myturb.params['wind_reference_speed'] = 11.0
myturb.params['wind_reference_height'] = 119.0

if __name__ == '__main__':

    #myturb.load(turbsave)
    myturb.set_optimizer('soga')
    myturb.set_options({'generations':1, 'population':2, 'restart':True, 'penalty':True, 'nstall':200, 'probability_of_mutation':0.4})
    myturb.prob.driver.add_objective('sm.load.structural_mass', scaler=1e-6)
    myturb = mysetup(myturb, False)
    myturb.run()
    myturb.save(turbsave)

