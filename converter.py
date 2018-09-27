import sys
import os
import glob
import cPickle as pickle
from floatingse.instance.spar_instance import SparInstance
from floatingse.instance.semi_instance import SemiInstance
from wisdem.floating.turbine_spar_instance import TurbineSparInstance
from wisdem.floating.turbine_semi_instance import TurbineSemiInstance
import numpy as np

plats = ('spar','semi','tlp')
objs = ('mass','cost')
mydtu = '10MW'


for plat in plats:
    for o in objs:
        os.chdir(plat+'-'+o)
        files = glob.glob('*.save')

        for fname in files:
            print plat+'-'+o+':', fname
            if fname.find('spar') >= 0:
                from baselineSpar import mysetup, mysub, myturb
                myobj = myturb if fname.find('turb') >= 0 else mysub
                max_draft = 200.0
                ncol = 0
                
            elif fname.find('semi') >= 0:
                from baselineSemi import mysetup, mysub, myturb
                myobj = myturb if fname.find('turb') >= 0 else mysub
                max_draft = 20.0
                ncol = 3
                
            elif fname.find('tlp') >= 0:
                from baselineTLP import mysetup, mysub, myturb
                myobj = myturb if fname.find('turb') >= 0 else mysub
                max_draft = 35.0
                ncol = 0
                
            else:
                raise Exception('Unknown platform')

            # FIFTH CONVERSTION
            with open(fname,'rb') as fp:
                oldobj = pickle.load(fp)
            oldparams, olddesvar, oldcons, oldobj, oldopt = oldobj

            newparams = myobj.params
            newparams['number_of_offset_columns'] = ncol
            for k in oldparams.keys():
                if k in newparams:
                    newparams[k] = oldparams[k]
                    
            with open(fname,'wb') as fp:
                pickle.dump((newparams, olddesvar, oldcons, oldobj, oldopt), fp)
                    
                    
            '''
            # FOURTH CONVERSION
            with open(fname,'rb') as fp:
                oldobj = pickle.load(fp)
            oldparams, olddesvar, oldcons, oldobj, oldopt = oldobj

            newparams = {}
            newparams['max_draft'] = max_draft
            for k in oldparams.keys():
                newkey = k
                newval = oldparams[k]
                if k == 'fairlead':
                    newkey = 'fairlead_location'
                    if oldparams['number_of_offset_columns'] > 0:
                        freeboard = oldparams['offset_freeboard']
                        h_section = oldparams['offset_section_height']
                    else:
                        freeboard = oldparams['main_freeboard']
                        h_section = oldparams['main_section_height']
                    z_nodes = np.flipud( freeboard - np.r_[0.0, np.cumsum(np.flipud(h_section))] )
                    newval = ((-newval) - z_nodes[0]) / (z_nodes[-1] - z_nodes[0])

                newparams[newkey] = newval
                
            newdesvar = []
            newcons = []
            for k in olddesvar:
                iadd = k[:]
                if k[0] == 'fairlead':
                    iadd = ['fairlead_location',0.0,1.0]
                newdesvar.append(iadd)

            for k in oldcons:
                if k[0].find('fairlead') >= 0: continue
                iadd = k[:]
                if k[0].find('draft_depth_ratio') >= 0:
                    ilab = k[0].replace('depth_ratio','margin')
                    iadd = [ilab,0.0,1.0,None]
                newcons.append(iadd)
            
            with open(fname,'wb') as fp:
                pickle.dump((newparams, newdesvar, newcons, oldobj, oldopt), fp)
            

            # THIRD CONVERSION
            with open(fname,'rb') as fp:
                oldobj = pickle.load(fp)
            oldparams, olddesvar, oldcons, oldobj, oldopt = oldobj
            newparams = {}
            for k in oldparams.keys():
                newkey = k.replace('ballast_heave_box','buoyancy_tank')
                newparams[newkey] = oldparams[k]

            newdesvar = []
            for k in olddesvar:
                iadd = k[:]
                iadd[0] = k[0].replace('ballast_heave_box','buoyancy_tank')
                newdesvar.append(iadd)

            with open(fname,'wb') as fp:
                pickle.dump((newparams, newdesvar, oldcons, oldobj, oldopt), fp)
                
            # SECOND CONVERSTION
            with open(fname,'rb') as fp:
                oldobj = pickle.load(fp)
            oldparams, olddesvar, oldcons, oldobj, oldopt = oldobj
            newparams = {}
            for k in oldparams.keys():
                newkey = k.replace('auxiliary','offset').replace('base','main')

                if newkey.startswith('sm.sg.'):
                    newkey = newkey[6:]
                elif newkey.startswith('sm.'):
                    newkey = newkey[3:]
                elif newkey.startswith('tcons.'):
                    newkey = newkey[6:]
                elif newkey.startswith('rotor.'):
                    newkey = newkey[6:]

                if newkey == 'safety_factor_frequency':
                    newkey = 'gamma_freq'
                    
                elif newkey == 'safety_factor_stress':
                    newkey = 'gamma_f'
                    
                elif newkey == 'safety_factor_materials':
                    newkey = 'gamma_m'
                    
                elif newkey == 'safety_factor_buckling':
                    newkey = 'gamma_b'
                    
                elif newkey == 'safety_factor_fatigue':
                    newkey = 'gamma_fatigue'
                    
                elif newkey == 'safety_factor_consequence':
                    newkey = 'gamma_n'
                    
                elif newkey == 'mooring_max_offset':
                    newkey = 'max_offset'
                    
                elif newkey == 'mooring_operational_heel':
                    newkey = 'operational_heel'

                elif newkey == 'sg.Rhub':
                    newkey = 'Rhub'

                    
                if newkey not in myobj.params:
                    print 'WARNING', newkey

                newparams[newkey] = oldparams[k]
                    

            newdesvar = []
            newcons   = []
            newobj    = []
            for k in olddesvar:
                iadd = k[:]
                if k[0].startswith('sm.'):
                    ilab = k[0][3:]
                elif k[0].startswith('tcons.'):
                    ilab = k[0][6:]
                elif k[0].startswith('rotor.'):
                    ilab = k[0][6:]
                else:
                    ilab = k[0]
                iadd[0] = ilab.replace('auxiliary','offset').replace('base','main')
                newdesvar.append(iadd)
                
            for k in oldcons:
                iadd = k[:]
                if k[0].startswith('sm.'):
                    ilab = k[0][3:]
                elif k[0].startswith('tcons.'):
                    ilab = k[0][6:]
                elif k[0].startswith('rotor.'):
                    ilab = k[0][6:]
                else:
                    ilab = k[0]
                    
                if ilab.startswith('subs.'):
                    ilab = ilab[5:]
                elif ilab.startswith('load.'):
                    ilab = ilab[5:]
                elif ilab.startswith('mm.'):
                    ilab = ilab[3:]
                elif ilab.startswith('sg.'):
                    ilab = ilab[3:]
                iadd[0] = ilab.replace('auxiliary','offset').replace('aux.','off.').replace('base','main').replace('_column_','_')
                newcons.append(iadd)

            if oldobj[0].startswith('sm.load.'):
                newobj = (oldobj[0][8:], oldobj[1])
            elif oldobj[0].startswith('sm.'):
                newobj = (oldobj[0][3:], oldobj[1])
            elif oldobj[0].startswith('load.'):
                newobj = (oldobj[0][5:], oldobj[1])
            else:
                newobj = oldobj
                

            with open(fname,'wb') as fp:
                pickle.dump((newparams, newdesvar, newcons, newobj, oldopt), fp)
            '''

            
            myobj.set_reference('10MW')
            myobj.load(fname)

            '''
            # FIRST CONVERSTION
            myobj.set_optimizer('nm')
            myobj.set_options({'penalty':True, 'restart':True, 'tol':1e-6, 'global_search':False})
            myobj.set_options({'generations':1, 'nstall':5, 'adaptive_simplex':True})
            myobj = mysetup(myobj, False)
            '''
            
            myobj.evaluate()
            #myobj.run()
            myobj.save(fname)
        
        
        os.chdir('..')
