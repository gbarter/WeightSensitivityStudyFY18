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
    mysub.set_options({'penalty':True, 'restart':True, 'tol':1e-6, 'global_search':False})
    mysub = mysetup(mysub, False)

    # Initialize containers
    m_rna_orig          = 672300.5303006992
    m_nacelle_orig      = 446036.25
    m_substructure_pert = []
    m_structure_pert    = []
    m_water_pert        = []
    V_displaced_pert    = []
    lcoe_pert           = []
    draft_pert          = []
    spar_pert           = []
    ballast_pert        = []
    vballast_pert       = []

    # Determine which perturbation to run
    pert   = [1.1, 1.0, 0.9, 0.75, 0.667, 0.5]
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
	#if p == 1.0: mysub.load(subsave)
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
            # Coarse
            mysub.set_options({'generations':2000, 'nstall':300, 'adaptive_simplex':False})
            mysub.run()
            mysub.save(fsave)
            move('heuristic.restart',frest)
            # Fine
            mysub.load(fsave)
            mysub.set_options({'generations':10000, 'nstall':600, 'adaptive_simplex':True})
            mysub.run()
            mysub.save(fsave)
            move('heuristic.restart',frest)
        mysub.load(fsave)
        mypromote(mysub, myturb)
        myturb.params['nac_mass'] = m
        myturb.save('turb-'+fsave)
        mysub.evaluate()
        myturb.evaluate()
        m_structure_pert.append( myturb.prob['sm.load.structural_mass'] )
        V_displaced_pert.append( myturb.prob['sm.subs.total_displacement'] )
        lcoe_pert.append( myturb.prob['lcoe'] )
        draft_pert.append( myturb.prob['sm.base.draft'] )
        spar_pert.append( myturb.prob['sm.base.spar_mass'] )
        ballast_pert.append( myturb.prob['sm.base.ballast_mass'] )
        vballast_pert.append( myturb.prob['sm.subs.variable_ballast_mass'] )
        if p==1.0:
            m_structure_orig    = myturb.prob['sm.load.structural_mass']
            V_displaced_orig    = myturb.prob['sm.subs.total_displacement']
            lcoe_orig           = myturb.prob['lcoe']

    d_rna          = np.array(mypert)*m_nacelle_orig - m_nacelle_orig
    d_structure    = np.array( m_structure_pert ) - m_structure_orig
    d_displaced    = np.array( V_displaced_pert ) - V_displaced_orig
    d_lcoe         = np.array( lcoe_pert ) - lcoe_orig
    print np.round(np.c_[d_rna, d_structure, d_displaced, d_lcoe])

