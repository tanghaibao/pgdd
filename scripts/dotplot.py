from preferences import * 
import matplotlib.ticker as ticker

# axis default
origin, axis_len = 0.09, .89
tpos = origin+axis_len/2

def xformat(x, pos=None):
    return r"$%d$" % abs(x)

def xformat_mb(x, pos=None):
    return r"$%d\rm{M}$" % abs(x/1000000)

def startpos(list):
    n = 0
    newlist = []
    for num in list:
        n += num
        newlist.append(n)
    return newlist

def de_pseudo(i, j, START_POS_x, START_POS_y, atn):
    pseudo_starteri, pseudo_starterj = 0, 0
    try:
        if i == 1: pseudo_starteri = 0
        else: pseudo_starteri = START_POS_x[i-2]
        pseudo_starterj = START_POS_y[atn-j]
    except:
        pass
    #assert False, "\t".join(str(x) for x in (i,j,START_POS_x,START_POS_y,atn))
    return pseudo_starteri, pseudo_starterj

def get_tickrange(pre):
    tickrange = []
    for i in xrange(len(pre)-1):
        tickrange.append((pre[i] + pre[i+1])/2)
    return tickrange

def dotplot1(req):
    try:
        species1 = req.form.getfirst('sp1')
        species2 = req.form.getfirst('sp2')
    except:
        return "<font color='red'>Please select species from both lists.</font>"
    try: block = int(req.form.getfirst('block'))
    except: block = 0
    try: chr_filter = int(req.form.getfirst('chr_filter'))
    except: chr_filter = 0
    try: ks_filter = int(req.form.getfirst('ks_filter'))
    except: ks_filter = 0
    try: bp = int(req.form.getfirst('bp'))
    except: bp = 0
    if chr_filter:
        chr1 = int(req.form.getfirst('chr1'))
        chr2 = int(req.form.getfirst('chr2'))
    if species1>species2:
        species1,species2=species2,species1
        if (not block) and chr_filter: chr1,chr2=chr2,chr1
    sql1 = "SELECT block_no,chr_1,id_1,chr_2,id_2 from block WHERE note='%s_%s' AND chr_1 is not NULL AND chr_2 is not NULL"%(species1,species2)
    if bp:
        sql1 = "SELECT block_no,chr_1,end5_1,chr_2,end5_2 from block WHERE note='%s_%s' AND chr_1 is not NULL AND chr_2 is not NULL"%(species1,species2)
    results = myconnect(sql1)
    if results==-1: return DB_FAIL_MSG
    if len(results)==0 or "cp" in (species1, species2): 
        return "<font color='red'>Sorry, we are not able to visualize %s-%s data right now (perhaps one of the genome does not have pseudo-chromosomes)</font>"%(species1,species2)
    if chr_filter or ks_filter: sql1+=" AND"
    # sql where clause conditions
    cond1, cond2 = "", ""
    if chr_filter: 
        if species1==species2 and chr1>chr2: chr1, chr2 = chr2, chr1
        cond1 = " chr_1=%d AND chr_2=%d"%(chr1,chr2)
    ks = 0 
    ks_low = ks_high = None
    if ks_filter:
        try:
            ks_low = float(req.form.getfirst('ks1'))
            ks_high = float(req.form.getfirst('ks2'))
        except:
            return "Invalid input for Ks range."
        ks = 1
    if ks: cond2 = """ ks BETWEEN %s AND %s"""%(ks_low,ks_high)
    if cond1 and cond2: sql1+=cond1+' AND'+cond2
    else: sql1+=cond1+cond2

    fig, canvas, root = fig_init([8,8])
    ax = fig.add_axes([origin, origin, axis_len, axis_len])
    if chr_filter: return plot2(sql1,root,ax,canvas,fig,chr1,chr2,ks,species1,species2,ks_low,ks_high,bp)
    else: return plot1(sql1,root,ax,canvas,fig,ks,species1,species2,ks_low,ks_high,bp)

def plot1(sql1, root, ax, canvas, fig, ks, species1,species2,ks_low,ks_high,bp):
    # length list, label list, br is x-axis, at is y-axis
    #br_length, at_length = ctg_len[species1], ctg_len[species2]
    br_length, at_length = get_ctg_len(species1, bp), get_ctg_len(species2, bp)
    brn, atn = len(br_length), len(at_length)
    br_chr, at_chr = [], []
    for i in xrange(brn): br_chr.append('C%d'%(i+1))
    for i in xrange(atn): at_chr.append('C%d'%(i+1))
    br_max, at_max = sum(br_length), sum(at_length)
    br_whole = [0,br_max]
    at_whole = [0,at_max]
    START_POS_x = startpos(br_length)
    START_POS_y = startpos(reversed(at_length))
    # pull the dataset
    x = [];y = []
    results = myconnect(sql1)
    if results==-1: return DB_FAIL_MSG
    for datum in results:
        i, j = int(datum[1]),int(datum[3])
        pseudo_starteri, pseudo_starterj = de_pseudo(i,j,START_POS_x,START_POS_y,atn)
        xj, yj = pseudo_starteri+int(datum[2]), pseudo_starterj-int(datum[4])
        if species1==species2 and xj+yj>br_max: xj,yj=br_max-yj,br_max-xj
        x.append(xj)
        y.append(yj)
    START_POS_TICK_x = [0] + START_POS_x
    START_POS_TICK_y = [0] + START_POS_y
    tickrange_x = get_tickrange(START_POS_TICK_x)
    tickrange_y = get_tickrange(START_POS_TICK_y)

    ax.plot(x,y,'g.',alpha=.5,ms=1)

    for i in xrange(1, brn): ax.plot([START_POS_x[i-1], START_POS_x[i-1]], at_whole, 'm-')
    for i in xrange(1, atn): ax.plot(br_whole, [START_POS_y[i-1], START_POS_y[i-1]], 'm-')
    ax.set_xticks(tickrange_x)
    ax.set_xticklabels(br_chr)
    setp(ax.get_xticklabels(),rotation=45,color='b')
    ax.set_yticks(tickrange_y)
    ax.set_yticklabels(at_chr[::-1],color='b')
    if species1==species2: 
        ax.plot(br_whole,[at_whole[1],0],'r-')
        ax.plot([br_max-_ for _ in y],[br_max-_ for _ in x],
                '.',color="gray",alpha=.5,ms=1)

    ax.set_xlim(br_whole)
    ax.set_ylim(at_whole)
    # species name print
    root.text(.015,tpos,sp_dict[species2],fontweight="bold",ha="center",va="center",rotation=90)
    root.text(tpos,.015,sp_dict[species1],fontweight="bold",ha="center",va="center")
    for t in ax.get_xticklines() + ax.get_yticklines():
        t.set_visible(False)

    fa, fi = fig_terminate(root, canvas)
    map_name = "map_%s_%s" % (species1, species2)
    s = "<map name='%s'>" % map_name
    o = [640*origin,640*(1-origin)] # origin
    ax_l = 640*axis_len # ax length in px
    # map start_pos_tick list to coords value
    sptx, spty = [x*1./sum(br_length) for x in START_POS_TICK_x],[x*1./sum(at_length) for x in START_POS_TICK_y]
    for j in xrange(brn):
        for k in xrange(atn):
            p1,p2,p3,p4=o[0]+sptx[j]*ax_l,o[1]-spty[atn-k]*ax_l,o[0]+sptx[j+1]*ax_l,o[1]-spty[atn-k-1]*ax_l
            alt_text = "Zoom in %s%d-%s%d"%(species1,j+1,species2,k+1)
            s+="<area shape='rect' href='javascript:talktoServer_block(%d,%d);' title='%s' coords='%i,%i,%i,%i' alt='%s'></area>"%(j+1,k+1,alt_text,p1,p2,p3,p4,alt_text)
    s += "</map>"
    s += "%d pairs of anchors plotted " % len(results)
    if ks: 
        s += "(ks filter: %.1f to %.1f) " % (ks_low, ks_high)
    s += "<font color='red'> click </font> on block to zoom in <br /><img class='articleimg' src='/duplication/usr/%s' usemap='#%s' alt='' /><br />" % (fi, map_name)
    img_location = "/duplication/scripts/to_pdf?imagename=%s" % fa
    return s + "&nbsp;<img src='/duplication/images/icons/pdf.png' onclick=\"window.location.href='%s';\" alt='Export to pdf' />" % img_location + print_button

def plot2(sql1, root, ax, canvas, fig, chr1, chr2, ks, species1,species2,ks_low,ks_high,bp):
    # length list, label list, br is x-axis, at is y-axis
    #br_length, at_length = ctg_len[species1], ctg_len[species2]
    br_length, at_length = get_ctg_len(species1,bp), get_ctg_len(species2,bp)
    br_max, at_max = br_length[chr1-1], at_length[chr2-1]
    br_whole = [0,br_max]
    at_whole = [0,at_max]
    # pull the dataset
    x = [];y = []
    results = myconnect(sql1)
    if results==-1: return DB_FAIL_MSG
    s = "<button onclick='talktoServer();'>Back to whole genome comparison</button><br />"
    if len(results)==0: return s+"No anchor points found for %s Chr%i and %s Chr%i"%(species1,chr1,species2,chr2)
    ymax = at_length[chr2-1]
    for datum in results:
        xj,yj = int(datum[2]),-int(datum[4])
        if chr1==chr2 and species1==species2 and xj+yj>0: xj,yj = -yj,-xj
        x.append(xj)
        y.append(yj)

    ax.plot(x,y,'g.',ms=2)

    if chr1==chr2 and species1==species2: 
        ax.plot(br_whole,[0,-at_max],'r-')
        ax.plot([-_ for _ in y],[-_ for _ in x],'.',color="gray",ms=2)
    
    _xformat = xformat
    if bp: _xformat = xformat_mb
    
    # put the units onto the axis, pay attention to y-axis, as it is inverted
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(_xformat))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_xformat))
    ax.set_xlim(br_whole)
    ax.set_ylim([-ymax, 0])
    ax.grid(color="k",alpha=.2,ls=":")
    # species name print
    root.text(tpos,.015,sp_dict[species1]+" Chr%d"%chr1,fontweight="bold",ha="center",va="center")
    root.text(.015,tpos,sp_dict[species2]+" Chr%d"%chr2,fontweight="bold",ha="center",va="center",rotation=90)

    fa, fi = fig_terminate(root, canvas)
    if ks: s+="%i pairs of anchor points plotted (ks filter: %s to %s) <br />"%(len(results),ks_low,ks_high)
    else: s+="%i pairs of anchor points plotted <br />"%len(results)
    s+="<a href='/duplication/index/block_details?chr_low=%i&amp;chr_high=%i&amp;note=%s_%s' target='_blank'><img class='articleimg' src='/duplication/usr/%s' title='Click to view all segments in this plot' alt='Click to view all segments in this plot' /></a><br />"%(chr1,chr2,species1,species2,fi)
    img_location = "/duplication/scripts/to_pdf?imagename=%s" % fa
    return s+"&nbsp;<img src='/duplication/images/icons/pdf.png' onclick=\"window.location.href='%s';\""\
            "alt='Export to pdf' />" % img_location + print_button
