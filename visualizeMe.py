#from __future__ import print_function
#from builtins import *
import sys

import floatingse.instance
import wisdem
import rotorse
from floatingse.instance.spar_instance import SparInstance
from floatingse.instance.semi_instance import SemiInstance
from wisdem.floating.turbine_spar_instance import TurbineSparInstance
from wisdem.floating.turbine_semi_instance import TurbineSemiInstance

mydtu = '10MW'
mydict = {1:'spar-soga.save', 2:'semi-soga.save', 3:'tlp-soga.save', 4:'turb-spar-soga.save', 5:'turb-semi-soga.save'}


def name2obj(fstr):
    if not type(fstr) == type('') or type(fstr) == type(u''):
        raise ValueError(str(fstr)+' is not a valid string')
    mystr = fstr.lower()
    
    if mystr.find('turb') >= 0 and mystr.find('spar') >= 0:
        myobj = TurbineSparInstance(mydtu)
    elif mystr.find('turb') >= 0 and (mystr.find('semi') >= 0 or mystr.find('tlp') >= 0):
        myobj = TurbineSemiInstance(mydtu)
    elif mystr.find('turb') < 0 and mystr.find('spar') >= 0:
        myobj = SparInstance()
    elif mystr.find('turb') < 0 and (mystr.find('semi') >= 0 or mystr.find('tlp') >= 0):
        myobj = SemiInstance()
    else:
        raise ValueError('Unknown solution, '+fstr)

    myobj.set_reference('10MW')
    myobj.load(fstr)
    myobj.evaluate()
    myobj.constraint_report()
    try:
        print 'mass', 1e-6*myobj.prob['structural_mass']
        print 'cost', 1e-6*myobj.prob['total_cost']
        print 'R_fairlead', myobj.prob['fairlead_radius']
        print 'R_aux', myobj.params['radius_to_offset_column']
    except:
        pass
    return myobj

if __name__ == '__main__':
    if len(sys.argv) != 2: raise Exception('Must pass in save-file')
    myobj = name2obj( sys.argv[1] )
    myobj.visualize()
    
    
