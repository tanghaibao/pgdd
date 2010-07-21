import sys
import os.path as op
import matplotlib
matplotlib.use('Agg')

from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from pylab import * 

sys.path.insert(0, op.join(op.dirname(__file__), ".."))
from preferences import myconnect

import itertools
import os


# generate data file
sql = "SELECT note, ks FROM block"
results = list(myconnect(sql))
results.sort()

fontdict = {"color":"b", "fontweight":"bold", "size":10}

def my_hist(l, interval, max_r, c):
    n = []; p = []
    total_len = len(l)
    if total_len==0: return 0
    for i in arange(0, max_r, interval):
        xmin, xmax = i-.5*interval, i+.5*interval
        nx = [x for x in l if xmin<=x<xmax]
        n.append(i)
        p.append(len(nx)*100./total_len)
    ax.set_xlabel('Synonymous substitutions per site (Ks)', fontdict)
    ax.set_ylabel('Percentage of %d gene pairs'%total_len, fontdict)

    xs, ys = poly_between(n, 0, p)
    return ax.fill(xs, ys, fc='g', alpha=.3)

species = {"at":"Arabidopsis",
           "bd":"Brachypodium",
           "pp":"Peach",
           "os":"Rice",
           "cp":"Papaya",
           "pt":"Poplar",
           "vv":"Grape",
           "sb":"Sorghum",
           "mt":"Medicago",
           "gl":"Soybean",
           "zm":"Maize"}

def lognormpdf(bins, mu, sigma):
    return exp(-(log(bins)-mu)**2/(2*sigma**2))/(bins*sigma*sqrt(2*pi))

def lognormpdf_mix(bins, probs, mus, variances):
    y = 0
    for i in xrange(components):
        y += probs[i]*lognormpdf(bins, mus[i], sqrt(variances[i]))
    y*=10
    return y

def get_mixture(data, components):
    #probs  = [.476, .509];mus    = [.69069, -.15038]
    #variances = [.468982e-1, .959052e-1]
    probs = []; mus = []; variances = []
    fw = file("temp_data","w")
    log_data = [log(x) for x in data if x>.05]
    fw.write("\n".join(["%.4f"%x for x in log_data]).replace("inf\n",""))
    fw.close()
    pipe = os.popen("./gmm-bic %d %d temp_data"%(components, len(log_data)))
    for row in pipe:
        if row.startswith("#"):
            atoms = row.split(",")
            mus.append(float(atoms[1]))
            variances.append(float(atoms[2])**2)
            probs.append(float(atoms[3]))
            
    return probs, mus, variances

def xformat(x, pos=None):
    return r"$%.1f$" % x

def yformat(x, pos=None):
    return r"$%d$" % x

# plot
for pair, data in itertools.groupby(results, key=lambda x:x[0]): 
    data = [x[1] for x in data if (.005 < x[1] < 3)]
    fig = matplotlib.figure.Figure(figsize=(4,4))
    canvas = FigureCanvas(fig)
    ax = fig.add_axes([.12,.1,.8,.8])
    
    print "plot pair", pair
    ksrange = (0, 3)
    line_at = my_hist(data, .1, 3.0, 'g')
    print "total %d pairs" % len(data)
    if line_at==0: continue

    # get mixture
    if pair=="at_at" or pair=="pt_pt" or pair=="gl_gl" or pair=="zm_zm": 
        components = 2
    #elif pair=="mt_mt": components = 2
    else: components = 1
    probs, mus, variances = get_mixture(data, components)

    bins = arange(0.001, 3.0, .001)
    y = lognormpdf_mix(bins, probs, mus, variances)

    line_at_mixture = ax.plot(bins, y, 'r:', lw=3)
    for i in xrange(components):
        peak_val = exp(mus[i])
        ax.text(peak_val, lognormpdf_mix(peak_val, probs, mus, variances), \
                "Ks=%.2f (%d%%)"%(peak_val, int(round(probs[i]*100))), \
                color="w", size=10, bbox=dict(ec='w',fc='r',alpha=.6))

    ax.set_xlim(ksrange)
    a, b = [species[x] for x in pair.split("_")]
    ax.set_title('%s vs %s Ks distribution'%(a,b), fontweight="bold", size=11)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(xformat))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(yformat))
    fl = '/var/www/duplication/images/ks_img/%s_ks.png' % pair
    #fl = "images/%s_ks.png" % pair
    dpi = 90
    canvas.print_figure(fl,dpi=dpi)
    del fig

os.remove('temp_data')
rcdefaults()
