from wisdem.floating.turbine_semi_instance import TurbineSemiInstance
import numpy as np
from shutil import copyfile, move
import os
import sys
from baselineSpar import mypromote


fdefault = 'sub-nm.save'

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

    # Save name override
    overrideName = os.path.exists(fdefault)
    if overrideName:
        subsave     = fdefault
        restartFlag = True
        plotFlag    = False

    # Load optimized turbine baseline
    mysub.load(subsave)
    mysub.evaluate()

    # Initialize optimization
    mysub.set_optimizer('nm')
    mysub.set_options({'penalty':True, 'restart':True, 'adaptive_simplex':False, 'tol':1e-6, 'global_search':False})
    mysub.set_options({'generations':1000, 'nstall':200})
    mysub = mysetup(mysub, False)

    # Initialize containers
    m_rna_orig          = 672300.5303006992
    m_nacelle_orig      = 446036.25

    # Determine which perturbation to run
    #pert   = [1.1, 1.0, 0.9, 0.75, 0.667, 0.5]
    pert   = [0.75]
    mypert = None
    for p in pert:
        pstr = str(p).replace('.','p')
        if mycwd.find(pstr) >= 0:
            mypert = [p]
            break
    if mypert is None:
        if overrideName:
            raise Exception('Are you running a single perturbation? Check file and symlink setup.')
        mypert = pert
    print 'Running this perturbation set:', mypert

    for p in mypert:
        m = p * m_nacelle_orig
        pstr = str(p).replace('.','p')
        fsave = fdefault if overrideName else subsave.replace('.save','_'+pstr+'.save').replace('soga','nm')
        frest = fsave.replace('save','restart')
	if os.path.exists(fsave): mysub.load(fsave)
        if restartFlag and os.path.exists(frest):
            copyfile(frest,'heuristic.restart')
        if not os.path.exists(fsave) or restartFlag:
	    print 'RUNNING', str(p)
            mysub.params['rna_mass'] = m_rna_orig - (m_nacelle_orig - m)
            mysub.run()
            mysub.save(fsave)
            move('heuristic.restart',frest)
        mysub.load(fsave)
        mypromote(mysub, myturb)
        myturb.params['nac_mass'] = m
        myturb.save('turb-'+fsave)
