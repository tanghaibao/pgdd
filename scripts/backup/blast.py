from preferences import *
from numpy import arange
from tempfile import mkstemp
from operator import itemgetter

def to_mb(l, mb):
    return l*mb/10000000.

def plot_map(hits, sp):
    fig, canvas, root = fig_init([8,4])
    # species name
    root.text(.5,1.,sp_dict[sp],fontweight="bold",ha="center",va="top")
    # retrieve the lengths of chrs and estimate the gauge
    chr_len = ctg_bp[sp]
    if not chr_len: return "<font color='red'>There are no pseudomolecules for %s data yet.</font>"%sp
    gauge = (max(chr_len)/10000000+1)*10 # in Mb
    mb = 7./gauge
    chr_num = len(chr_len)
    xstart, ystart, tip = .04, .9, .008
    xtop, ytop = xstart, ystart
    xincre = 1./(chr_num+1.5) # distance between chrs
    yincre = .2*mb
    # draw the gauge
    root.plot([xstart,xstart],[ystart,ystart-.7],"b-")
    for x in xrange(0, gauge+2, 2):
        if x%10:
            root.plot([xstart,xstart+tip],[ystart, ystart],"b-")
        else:
            root.plot([xstart-tip,xstart+tip],[ystart,ystart],"b-")
            root.text(xstart+tip+.005,ystart,str(x),verticalalignment="center")
        ystart -= yincre
    root.text(xstart+tip+.005,.15,"Mb",verticalalignment="center")
    # draw chromosomes
    chr_width = .015
    for i, l in enumerate(chr_len):
        xstart += xincre
        cl = to_mb(l, mb) # chromosome length
        root.add_patch(Rectangle((xstart,ytop-cl),chr_width,cl,\
                ec="k",fc="k"))
        for x in arange(.8,0,-.16):
            root.add_patch(Rectangle((xstart,ytop-cl),chr_width*x,cl,\
                    lw=0,fc="w",alpha=.35))
        root.text(xstart+.5*chr_width,ytop+chr_width,"%d"%(i+1),\
                horizontalalignment="center")
    
    # ticks for the genes
    for a, b, e, s in hits:
        b = b.split(".")[0].capitalize()
        sql1 = "SELECT chromo, end5 FROM loci WHERE locus='%s'"%b
        results = myconnect(sql1)
        if results==-1: return DB_FAIL_MSG
        ch, pos = results[0]
        ch, pos = ch.replace("chr",""), to_mb(int(pos),mb)
        # 'Vv15r', 'ctg41' ...
        try: ch = int(ch)
        except: continue
        root.plot([xtop+xincre*ch+chr_width, xtop+xincre*ch+chr_width+tip],\
                [ytop-pos, ytop-pos], "g-")

    fa, fi = fig_terminate(root, canvas)
    return "<img src='/duplication/usr/%s' class='articleimg' alt='' />"%fi

def blast1(req):
    """blast commandline to run blastall with three use-input params
    """
    database = "all"
    seq = req.form.getfirst('seq')
    id = req.form.getfirst('id')
    filter = req.form.getfirst('filter')
    evalue = req.form.getfirst('evalue')
    program = req.form.getfirst('program')
    # default value
    if not program: program="blastp"
    if not filter: filter="T"
    if not evalue: evalue="1e-10"
    tmp_fd, tmp_fn = mkstemp()
    fw = os.fdopen(tmp_fd, "w")
    if seq.startswith(">"): fw.write(seq)
    elif id: fw.write(">%s\n%s"%(id, seq))
    else: fw.write(">%s\n%s"%("usr_seq",seq))
    fw.close()
    # run blastall command
    res = os.popen("blastall -i %s -d /var/www/duplication/data/%s -e %s -T T -p %s -F %s -m8 |cut -f1,2,11,12"%(tmp_fn, database, evalue, program, filter)).read()
    os.remove(tmp_fn)
    hits = set([tuple(x.split()) for x in res.splitlines()])
    if not hits: return "<font color='red'>No blast hits are found.</font>"
    sp = sp_dict.keys() 
    sp_hits = {}
    for s in sp: 
        ss = s
        if s=="bd": ss="br"
        sp_hits[s] = [x for x in hits if x[1][:2].lower()==ss]
    page_rank = []
    for k,v in sp_hits.items():
        if v: page_rank.append([max([float(x[-1]) for x in v]),k])
        else: page_rank.append([0,k])
    k_rank = [x[1] for x in reversed(sorted(page_rank))]
    msg = "All hits are displayed as ticks along the chromosomes for each of the genomes."
    i = 0 
    for k in k_rank:
        hits = sp_hits[k]
        if hits: i+=1
        else: continue
        hits.sort(key=itemgetter(1))
        msg += "<hr /> [%d] %d hits in %s genome.<br />"%(i, len(hits), sp_dict[k])
        msg += "<font color='green'>%s</font><br />"%("  ".join(["%s(%s)"%(b,c) for a,b,c,d in hits]))
        msg += plot_map(hits,k)
    return msg+"<hr /><br />"+print_button
