from wisdem.floating.turbine_semi_instance import TurbineSemiInstance
import numpy as np
from shutil import copyfile, move
import os
import sys
from baselineSpar import mypromote



if __name__ == '__main__':
    # Determine which substructure we are using
    mycwd = os.getcwd()
    if mycwd.lower().find('spar') >= 0:
        from baselineSpar import mysetup, subsave, turbsave, mysub, myturb
    elif mycwd.lower().find('semi') >= 0:
        from baselineSemi import mysetup, subsave, turbsave, mysub, myturb
    elif mycwd.lower().find('tlp') >= 0:
        from baselineTLP import mysetup, subsave, turbsave, mysub, myturb
    else:
        raise Exception('Unknown substructure type.  Use: spar / semi / tlp')

    restartFlag = sys.argv[-1].lower().find('restart') >= 0

    # Load optimized turbine baseline
    mysub.load(subsave)
    mysub.evaluate()

    # Initialize containers
    m_rna_orig          = 672300.5303006992
    m_nacelle_orig      = 446036.25

    # Determine which perturbation to run
    pert   = [1.1, 1.0, 0.9, 0.75, 0.667, 0.5]
    #pert.reverse()
    print 'Running this perturbation set:', pert

    for p in pert:
        m = p * m_nacelle_orig
        pstr = str(p).replace('.','p')
        fsave = subsave.replace('.save','_'+pstr+'.save').replace('v0','v2')
        frest = fsave.replace('save','restart')
        
        if not os.path.exists(fsave) or restartFlag:
            repeatCounter = 0
            while True and repeatCounter < 11:
                print 'RUNNING', str(p)
                if os.path.exists(fsave): mysub.load(fsave)
                if restartFlag and os.path.exists(frest):
                    copyfile(frest,'heuristic.restart')
                mysub.params['rna_mass'] = m_rna_orig - (m_nacelle_orig - m)

                if repeatCounter < 1:
                    mysub.set_optimizer('subplex')
                    mysub.set_options({'penalty':True, 'tol':1e-6, 'global_search':False, 'penalty_multiplier':1e5})
                    mysub.set_options({'generations':40, 'nstall':8, 'restart':False, 'adaptive_simplex':False})
                elif repeatCounter < 3:
                    mysub.set_optimizer('nm')
                    mysub.set_options({'penalty':True, 'tol':1e-6, 'global_search':False, 'penalty_multiplier':1e5})
                    mysub.set_options({'generations':2000, 'nstall':200, 'restart':False, 'adaptive_simplex':False})
                else:
                    mysub.set_optimizer('nm')
                    mysub.set_options({'penalty':True, 'tol':1e-6, 'global_search':False, 'penalty_multiplier':1e5})
                    mysub.set_options({'generations':3000, 'nstall':750, 'restart':True, 'adaptive_simplex':True})

                mysub = mysetup(mysub, False)
                mysub.run()
                mysub.save(fsave)
                copyfile('heuristic.restart',frest)
	    
                passFlag = mysub.constraint_report(printFlag=False)
                print 'Counter:', repeatCounter, '  Passing:', passFlag
                if passFlag: break
                repeatCounter += 1

        mysub.load(fsave)
        mypromote(mysub, myturb)
        myturb.params['nac_mass'] = m
        myturb.save('turb-'+fsave)
        mysub.evaluate()
        myturb.evaluate()


