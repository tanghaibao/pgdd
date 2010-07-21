import cgi
import os
os.environ['HOME']='/var/www/duplication/usr/'
import MySQLdb
from random import randint
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from pylab import setp, rcdefaults, xticks, yticks, get
from matplotlib.patches import Arrow, Rectangle, Polygon

print_button = "&nbsp;<img src='/duplication/images/icons/print.png' onclick='window.print();' alt='Print this page' />"

sp_dict = dict(at="Arabidopsis",os="Rice",pt="Poplar",mt="Medicago",vv="Grape",cp="Papaya",sb="Sorghum",gl="Soybean",bd="Brachypodium",zm="Maize", pp="Peach")

DB_FAIL_MSG = "<font color='red'>SQL server temporarily inaccessible. Please refresh this page, or check back later.</font>"
def myconnect(sql):
    try: mycon = MySQLdb.Connect(user='',passwd='',db='')
    except: return -1
    mycursor = mycon.cursor()
    mycursor.execute(sql)
    results = mycursor.fetchall()
    mycon.close()
    return results


def get_ctg_len(species, bp=0):
    sql = "select chromo, max_id from ctg_len where sp='%s'" % species
    if bp:
        sql = "select chromo, max_bp from ctg_bp where sp='%s'" % species
    results = myconnect(sql)
    results = sorted([(int(c[3:]), id) \
            for (c, id) in results if c[-1]!="r"])
    return [x[1] for x in results]


def fig_init(size):
    fig = matplotlib.figure.Figure(figsize=size)
    canvas = FigureCanvas(fig)
    root = fig.add_axes([0,0,1,1])
    return fig, canvas, root

def fig_terminate(root, canvas):
    root.set_xlim([0,1])
    root.set_ylim([0,1])
    root.set_axis_off()
    fa = "tmp_%05d" % randint(0, 100000)
    fi = fa+".png"
    fl = "/var/www/duplication/usr/"+fi
    canvas.print_figure(fl,dpi=80)
    canvas.print_figure(fl.replace("png", "pdf"))
    return fa, fi
