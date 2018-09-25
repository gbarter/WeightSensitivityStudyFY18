import numpy as np
import os
import sys
from matplotlib import pyplot as plt
import plotTools as pt
from baselineSpar import mysub as myspar
from baselineSemi import mysub as mysemi
from baselineTLP0 import mysub as mytlp
import cPickle as pickle        
import csv

mycolors = plt.rcParams['axes.prop_cycle'].by_key()['color']

def myave(x, y):
    return (np.trapz(y,x) / (x[-1] - x[0]))

class MyMetric(object):
    def __init__(self, tag, probStr, labStr, unitStr, scale, vec=False):
        self.tag = tag
        self.label = labStr
        self.units = unitStr
        self.scale = scale
        self.vec   = vec
        if isinstance(probStr, list):
            self.probCodes = probStr
        elif type(probStr) == type(''):
            self.probCodes = [probStr]

metrics = [MyMetric('mass', 'load.structural_mass', 'Substructure mass', '[1000t]', 1e-6),
           MyMetric('volume', 'subs.total_displacement','Substructure displacement', '[k$m^3$]', 1e-3),
           MyMetric('cost', 'total_cost', 'Substructure cost', '[M USD]', 1e-6),
           MyMetric('mball_base', 'base.ballast_mass', 'Substructure main ballast mass', '[t]', 1e-3),
           MyMetric('mball_aux', 'aux.ballast_mass','Substructure offset ballast mass', '[t]', 1e-3),
           MyMetric('cball_base', 'base.ballast_cost','Substructure main ballast cost', '[M USD]',1e-6),
           MyMetric('cball_aux', 'aux.ballast_cost','Substructure offset ballast cost', '[M USD]',1e-6),
           MyMetric('mcol_base', 'base.total_mass','Substructure main col mass', '[1000t]',1e-6),
           MyMetric('mcol_aux', 'aux.total_mass','Substructure offset col mass', '[1000t]',1e-6),
           MyMetric('ccol_base', 'base.total_cost','Substructure main col costs', '[M USD]', 1e-6),
           MyMetric('ccol_aux', 'aux.total_cost','Substructure offset col costs', '[M USD]', 1e-6),
           MyMetric('water', 'subs.variable_ballast_mass','Substructure water ballast', '[1000t]',1e-6),
           MyMetric('mpont', 'load.pontoon_mass','Substructure pontoon mass', '[1000t]',1e-6),
           MyMetric('cpont', 'load.pontoon_cost','Substructure pontoon cost', '[M USD]',1e-6),
           MyMetric('cmoor', 'mooring_cost','Mooring cost', '[M USD]', 1e-6),
           MyMetric('based', 'base.d_full','', '[m]',1.0,True),
           MyMetric('basez', 'base.z_full','','[m]',1.0,True),
           MyMetric('baset', 'base.t_full','','[m]',1.0,True),
           MyMetric('auxd', 'aux.d_full','', '[m]',1.0,True),
           MyMetric('auxz', 'aux.z_full','','[m]',1.0,True),
           MyMetric('auxt', 'aux.t_full','','[m]',1.0,True),
           MyMetric('basedraft', 'base.draft','Main column draft', '[m]',1.0),
           MyMetric('auxdraft', 'aux.draft','Offset column draft', '[m]',1.0),
           MyMetric('tension', 'mm.neutral_load','Mooring downward force', '[MN]',1e-6),
           MyMetric('mball', ['base.ballast_mass','aux.ballast_mass'], 'Substructure column ballast mass', '[1000t]', 1e-6),
           MyMetric('cball', ['base.ballast_cost','aux.ballast_cost'], 'Substructure column ballast cost', '[M USD]', 1e-6),
           MyMetric('mcol',['base.total_mass','aux.total_mass'],
                    'Substructure column masses', '[1000t]',1e-6),
           MyMetric('ccol',['base.total_cost','aux.total_cost'],
                    'Substructure column costs', '[M USD]', 1e-6),
           MyMetric('baseaved', [],'Main column ave diameter', '[m]',1.0),
           MyMetric('auxaved', [],'Offset column ave diameter', '[m]',1.0),
           MyMetric('baseavet', [],'Main column ave thickness', '[mm]',1e3),
           MyMetric('auxavet', [],'Offset column ave thickness', '[mm]',1e3),
           MyMetric('csub', 'total_cost','Substructure cost w/o mooring', '[USV]',1e-9),
]
metnames = [im.tag for im in metrics]

objs = ['mass','cost']

platforms = [('spar',myspar),('semi',mysemi),('tlp',mytlp)]
m_rna_orig     = 672300.5303006992
m_nacelle_orig = 446036.25

pert   = [1.1, 1.0, 0.9, 0.75, 0.667, 0.5]
npert  = len(pert)
ibase  = pert.index(1.0)

delta_rna = m_nacelle_orig * (np.array(pert) - 1.0)

# Load all data
DATA_FILE = 'alldata.pkl'
if os.path.exists(DATA_FILE):
    with open(DATA_FILE,'rb') as fp:
        data = pickle.load(fp)
else:
    data = {}
    for platStr,plat in platforms:
        data[platStr] = {}
        for o in objs:
            data[platStr][o] = {}
            fdir = platStr + '-' + o
            os.chdir(fdir)

            # Standard, scalar metrics
            for im in metrics:
                if im.vec:
                    data[platStr][o][im.tag] = {}
                else:
                    data[platStr][o][im.tag] = np.nan * np.ones(npert)
                    data[platStr][o][im.tag] = data[platStr][o][im.tag].tolist()
            
            for k,p in enumerate(pert):
                pstr = str(p).replace('.','p')
                fname = platStr + '-nm_' + pstr + '.save'
                if not os.path.exists(fname): continue
                plat.load(fname)
                plat.evaluate()
                ncol = plat.prob['number_of_auxiliary_columns']
                for im in metrics:
                    if im.tag.find('aved') >= 0: continue

                    temp = 0.0
                    for probid in im.probCodes:
                        if probid.find('aux') >= 0 and len(im.probCodes)>1:
                            coeff = ncol
                        elif probid.find('aux') >= 0 and platStr in ['spar','tlp']:
                            coeff = 0.0
                        else:
                            coeff = 1.0
                        temp = temp + coeff*plat.prob[ probid ]
                    if not im.vec and not im.tag in ['tension']: temp = np.sum(temp)

                    if im.tag == 'tension':
                        temp = np.sum(temp[:,-1])
                    elif im.tag == 'mcol':
                        temp -= data[platStr][o]['mball'][k]
                    elif im.tag == 'ccol':
                        temp -= data[platStr][o]['cball'][k]
                    elif im.tag == 'csub':
                        temp -= data[platStr][o]['cmoor'][k]
                        
                    if im.vec:
                        data[platStr][o][im.tag][pstr] = temp.tolist()
                    else:
                        data[platStr][o][im.tag][k] = temp

                data[platStr][o]['baseaved'][k] = myave(data[platStr][o]['basez'][pstr],data[platStr][o]['based'][pstr])
                data[platStr][o]['auxaved'][k] = myave(data[platStr][o]['auxz'][pstr],data[platStr][o]['auxd'][pstr])
                data[platStr][o]['baseavet'][k] = myave(data[platStr][o]['basez'][pstr],data[platStr][o]['baset'][pstr])
                data[platStr][o]['auxavet'][k] = myave(data[platStr][o]['auxz'][pstr],data[platStr][o]['auxt'][pstr])
                        
            os.chdir('..')
    with open(DATA_FILE,'wb') as fp:
        pickle.dump(data, fp)


        
# All sensitivities
cs = ['b', 'g', 'r']
marks = ['o','s','*']
xlab  = ('$\Delta$ Nacelle mass', '[1000t]')
fig1,ax1 = pt.initFigAxis()
fig2,ax2 = pt.initFigAxis()
for o in objs:
    for im in metrics:
        if im.vec: continue
        fig1.clf()
        fig2.clf()
        ax1 = fig1.add_subplot(111)
        ax2 = fig2.add_subplot(111)
        for k, temp in enumerate(platforms):
            platStr,plat = temp
            labStr = platStr.upper()+'-'+o.upper()
            if im.tag.find('aux') >= 0 and platStr in ['spar','tlp']: continue
            y = np.array( data[platStr][o][im.tag] )
            ax1.plot(1e-6*delta_rna, im.scale*(y - y[ibase]), linestyle='-', marker=marks[k], color=mycolors[k], label=labStr)
            ax2.plot(np.array(pert)-1.0, y/y[ibase] - 1.0, linestyle='-', marker=marks[k], color=mycolors[k], label=labStr)
        ax1.legend()
        ax1.grid()
        ax1.set_xlabel(xlab[0] + ' ' + xlab[1])
        ax1.set_ylabel('$\Delta$ ' + im.label + ' ' + im.units)
        pt.format(ax1,mode='save')
        pt.save(fig1, o+'-'+im.tag,'all')

        pt.ytick_percent(ax2, ytick=ax2.get_yticks())
        pt.xtick_percent(ax2, xtick=ax2.get_xticks())
        ax2.grid()
        ax2.legend()
        ax2.set_xlabel(xlab[0])
        ax2.set_ylabel('$\Delta$ ' + im.label)
        pt.format(ax2,mode='save')
        pt.save(fig2, o+'-'+im.tag+'_perc','all')


# Ballast changes on one plot
fig1.clf()
fig2.clf()
ax1 = fig1.add_subplot(111)
ax2 = fig2.add_subplot(111)
for o in objs:
    im = metrics[ metnames.index('mball') ]

    for k, temp in enumerate(platforms):
        platStr,plat = temp
        labStr = platStr.upper()+'-'+o.upper()+' Perm Ballast'

        y = np.array( data[platStr][o][im.tag] )
        ax1.plot(1e-6*delta_rna, im.scale*(y - y[ibase]), linestyle='-', marker=marks[k], color=mycolors[k], label=labStr)
        ax2.plot(np.array(pert)-1.0, y/y[ibase] - 1.0, linestyle='-', marker=marks[k], color=mycolors[k], label=labStr)

    im = metrics[ metnames.index('water') ]

    for k, temp in enumerate(platforms):
        platStr,plat = temp
        labStr = platStr.upper()+'-'+o.upper()+' Water Ballast'

        y = np.array( data[platStr][o][im.tag] )
        ax1.plot(1e-6*delta_rna, im.scale*(y - y[ibase]), linestyle='--', marker=marks[k], color=mycolors[k], label=labStr)
        ax2.plot(np.array(pert)-1.0, y/y[ibase] - 1.0, linestyle='--', marker=marks[k], color=mycolors[k], label=labStr)

    ax1.legend()
    ax1.grid()
    ax1.set_xlabel(xlab[0] + ' ' + xlab[1])
    ax1.set_ylabel('$\Delta$ Substructure Ballast ' + im.units)
    pt.format(ax1,mode='save')
    pt.save(fig1, o+'-allball','all')

    pt.ytick_percent(ax2, ytick=ax2.get_yticks())
    pt.xtick_percent(ax2, xtick=ax2.get_xticks())
    ax2.grid()
    ax2.legend()
    ax2.set_xlabel(xlab[0])
    ax2.set_ylabel('$\Delta$ Substructure Ballast')
    pt.format(ax2,mode='save')
    pt.save(fig2, o+'-allball_perc','all')


# Set cost premium
im = metrics[2]
fig,ax = pt.initFigAxis()
ax = fig.add_subplot(111)
for o in objs:
    #fig.clf()
    #ax = fig.add_subplot(111)
    lineStr = '-' if o=='mass' else '--'
    for k, temp in enumerate(platforms):
        platStr,plat = temp
        y = np.array( data[platStr][o][im.tag] )
        ax.plot(1e-6*delta_rna[2:], (y[2:] - y[ibase])/delta_rna[2:], linestyle=lineStr, color=mycolors[k], marker=marks[k], label=platStr.upper()+'-'+o.upper())

ax.set_ylim([0, 1500])
ax.set_yticks(np.arange(0,1501,300))
ax.legend()
ax.grid()
ax.set_xlabel(xlab[0] + ' ' + xlab[1])
ax.set_ylabel('Breakeven cost premium [USD/kg]')
pt.format(ax,mode='save')
#pt.save(fig, o+'-premium','all')
pt.save(fig, 'all-premium','all')

    
# Line plots
lines = ['-','--','-.']
labs = ['Baseline','75% RNA mass','50% RNA mass']
myperts = [1.0, 0.75, 0.5]
for o in objs:
    for platStr,plat in platforms:
        fig.clf()
        ax = fig.add_subplot(111)
        for ip, p in enumerate(myperts):
            pstr = str(p).replace('.','p')
            x = np.array( data[platStr][o]['based'][pstr] )
            y = np.array( data[platStr][o]['basez'][pstr] )
            ax.plot(0.5*x, y, 'k', linestyle=lines[ip], label=labs[ip])
            ax.plot(-0.5*x, y, 'k', linestyle=lines[ip])
        ax.grid()
        ax.legend()
        pt.save(fig, platStr+'-'+o+'_base-drawings','all')

        if platStr == 'semi':
            fig.clf()
            ax = fig.add_subplot(111)
            for ip, p in enumerate(myperts):
                pstr = str(p).replace('.','p')
                x = np.array( data[platStr][o]['auxd'][pstr] )
                y = np.array( data[platStr][o]['auxz'][pstr] )
                ax.plot(0.5*x, y, 'k', linestyle=lines[ip], label=labs[ip])
                ax.plot(-0.5*x, y, 'k', linestyle=lines[ip])
            ax.grid()
            ax.legend()
            pt.save(fig, platStr+'-'+o+'_aux-drawings','all')

# Fractional mass plots
barw = 0.8
bara = 0.8
mlabs = ['Columns','Permanent Ballast','Water Ballast','Pontoon']
clabs = ['Columns','Permanent Ballast','Mooring','Pontoon']
fig,ax = pt.initFigAxis()
for o in objs:
    mylabs = mlabs[:] if o == 'mass' else clabs[:]
        
    for platStr,plat in platforms:
        fig.clf()
        ax = fig.add_subplot(111)
        if o == 'mass':
            ymat  = np.c_[data[platStr][o]['mcol'], data[platStr][o]['mball'], data[platStr][o]['water'], data[platStr][o]['mpont']]
        else:
            ymat  = np.c_[data[platStr][o]['ccol'], data[platStr][o]['cball'], data[platStr][o]['cmoor'], data[platStr][o]['cpont']]
        ynorm = np.sum(ymat, axis=1)
        ymat  = ymat / ynorm[:,np.newaxis]
        ycum  = np.cumsum(ymat, axis=1)
        xval = np.arange(len(pert))
        for k in range(4):
            if k == 0:
                ax.bar(xval, ymat[:,0], width=barw, alpha=bara, label=mylabs[0])
            else:
                ax.bar(xval, ymat[:,k], bottom=ycum[:,k-1], width=barw, alpha=bara, label=mylabs[k])
        ax.set_xticks(xval)
        ax.set_xticklabels([str(m) for m in pert])
        ax.set_xlabel('RNA mass scaling')
        ax.set_ylabel('Substructure '+o+' fraction')
        ax.legend()
        pt.ytick_percent(ax)
        pt.format(ax,mode='save')
        pt.save(fig, platStr+'-'+o+'_fractions','all')


# Comparison table
ftmp   = 'temp.dat'
fout   = 'tableOut.dat'
outmat = []
labout = ['Metric']
metout = []
for platStr,plat in platforms:
    for o in objs:
        tempout = []
        labout.append(platStr+'-'+o)
        for im in metrics:
            if im.vec or im.tag in ['mpont','cpont','offset']: continue
            temp = np.round(im.scale * data[platStr][o][im.tag][ibase], 1)
            tempStr = str(temp) if temp > 0.0 else ''
            tempout.append(tempStr)
            if len(labout) == 2:
                metout.append(im.label+' '+im.units)
        outmat.append( tempout )
outmat = [list(i) for i in zip(*outmat)] # transpose

with open(ftmp, mode='w') as fcsv:
    writer = csv.writer(fcsv, delimiter='&')
    writer.writerow(labout)
    for im in range(len(metout)):
        writer.writerow([metout[im]]+outmat[im])

fread  = open(ftmp, mode='r')
fwrite = open(fout, mode='w')
for lineIn in fread:
    lineOut = lineIn.strip().replace('&',' & ') + '\\\\' + '\n'
    fwrite.write(lineOut)
fread.close()
fwrite.close()

