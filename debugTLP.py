from wisdem.floating.turbine_spar_instance import TurbineSparInstance
from floatingse.instance.tlp_instance import TLPInstance
import numpy as np
import offshorebos.wind_obos as wind_obos
from baselineTLP import mysetup

subsave    = 'tlp-soga.save'
turbsave   = 'turb-tlp-soga.save'
optstr     = 'psqp'
subsaveopt = subsave.replace('soga',optstr)

mysub = TLPInstance()
mysub.set_reference('10MW')
mysub.params['water_depth'] = 320.0
mysub.params['Hs'] = 10.8
mysub.params['T'] = 9.8
mysub.params['Uref'] = 11.0
mysub.params['zref'] = 119.0
mysub.params['mooring_max_offset'] = 100.0
mysub.params['mooring_type'] = 'nylon'
mysub.params['number_of_auxiliary_columns'] = 0

myturb = TurbineSparInstance('10MW')
myturb.set_reference('10MW')
myturb.params['water_depth'] = 320.0
myturb.params['wave_height'] = 10.8
myturb.params['wave_period'] = 9.8
myturb.params['wind_reference_speed'] = 11.0
myturb.params['wind_reference_height'] = 119.0
myturb.params['mooring_type'] = 'nylon'
myturb.params['anchor'] = wind_obos.Anchor.SUCTIONPILE
myturb.params['number_of_auxiliary_columns'] = 0


if __name__ == '__main__':

    #mysub.load(subsave)

    # SOGA
    mysub.set_optimizer('soga')
    mysub.set_options({'generations':5000, 'population':20, 'restart':False, 'penalty':True, 'nstall':300, 'probability_of_mutation':0.5})
    mysub.prob.driver.add_objective('total_cost', scaler=1e-6)
    mysub = mysetup(mysub)
    #mysub.run()
    #mysub.save(subsave)

    # Gradient
    #mysub.load(subsave)
    #mysub.set_optimizer(optstr)
    #mysub.prob.driver.add_objective('load.structural_mass', scaler=1e-6)
    #mysub = mysetup(mysub)
    #mysub.run()
    #mysub.save(subsaveopt)
    #mysub.load(subsaveopt)

    # Now shift to whole turbine
    for k in myturb.params.keys():
        if mysub.params.has_key(k):
            myturb.params[k] = mysub.params[k]
    myturb.load(turbsave)

    myturb.set_optimizer('soga')
    myturb.set_options({'generations':1, 'population':2, 'restart':True, 'penalty':True, 'nstall':200, 'probability_of_mutation':0.4})
    myturb.prob.driver.add_objective('sm.total_cost', scaler=1e-6)
    myturb = mysetup(myturb, False)
    myturb.run()
    myturb.save(turbsave)
    
