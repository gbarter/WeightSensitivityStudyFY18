import sys
import os
import glob

from floatingse.instance.spar_instance import SparInstance
from floatingse.instance.semi_instance import SemiInstance
from wisdem.floating.turbine_spar_instance import TurbineSparInstance
from wisdem.floating.turbine_semi_instance import TurbineSemiInstance

plats = ('spar','semi','tlp')
objs = ('mass','cost')
mydtu = '10MW'


for plat in plats:
    for o in objs:
        os.chdir(plat+'-'+o)
        files = glob.glob('*.save')

        for mystr in files:
            print plat+'-'+o+':', mystr
            if mystr.find('spar') >= 0:
                from baselineSpar import mysetup, mysub, myturb
                myobj = myturb if mystr.find('turb') >= 0 else mysub
                
            elif mystr.find('semi') >= 0:
                from baselineSemi import mysetup, mysub, myturb
                myobj = myturb if mystr.find('turb') >= 0 else mysub
                
            elif mystr.find('tlp') >= 0:
                from baselineTLP import mysetup, mysub, myturb
                myobj = myturb if mystr.find('turb') >= 0 else mysub
                #myobj = TurbineSparInstance(mydtu) if mystr.find('turb') >= 0 else SparInstance()
            else:
                raise Exception('Unknown platform')
            
            myobj.set_reference('10MW')
            myobj.load(mystr)

            myobj.set_optimizer('nm')
            myobj.set_options({'penalty':True, 'restart':True, 'tol':1e-6, 'global_search':False})
            myobj.set_options({'generations':1, 'nstall':5, 'adaptive_simplex':True})
            myobj = mysetup(myobj, False)
            
            myobj.evaluate()
            #myobj.run()
            myobj.save(mystr)
        
        
        os.chdir('..')
