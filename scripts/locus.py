from preferences import *

def get_details(lc):
    return "<a href='/duplication/index/details?lc=%s' target='_blank'>%s</a>"%(lc,lc)

def get_block_details(seg_id, lc, note):
    return "<a href='/duplication/index/block_details?seg_id=%s&amp;lc=%s&amp;note=%s' target='_blank'>"%(seg_id,lc,note)

def format_seq(seq, char_per_line=80):
    s = ''
    for i in xrange(len(seq)/char_per_line+1):
        s+=seq[i*char_per_line:(i+1)*char_per_line]+'<br />'
    s+=seq[(i+1)*char_per_line:]
    return s

def locus1(req):
    lc = cgi.escape(req.form.getfirst('lc')).strip().capitalize()
    try: sc = int(req.form.getfirst("sc"))
    except: sc = 100000
    if lc=="": return "<font color='red'>Please enter a non-empty ID.</font>"
    # Make SQL string and execute it
    sql1 = """SELECT block_no, note from block WHERE locus_1='%s' OR locus_2='%s'"""%(lc, lc)
    results = myconnect(sql1)
    if results==-1: return DB_FAIL_MSG
    if len(results)==0:
        lc_details = details1(req, lc)
        if lc_details.startswith('We'): data = lc_details
        else: data = "<font color='red'>The locus ( %s ) is not contained in any block.</font><br /><hr />%s"%(get_details(lc),lc_details)
        return data
    else:
        data = "All intra/cross-species blocks for %s, graphs and tables display <b><u>&plusmn;%dkb</u></b> region. Blue arrows are other anchor genes in the region, red is query locus.<br />"%(get_details(lc), sc/1000)
        si = 0 #seg
        for d in results:
            si+=1
            data+=show_seg(d[0],lc,d[1],si,sc)
        return data + "<br /><hr />" + print_button

def show_seg(seg_id,lc,note,si,sc):
    sql2 = """SELECT * from block WHERE block_no='%s' AND note='%s' ORDER BY end5_1"""%(seg_id,note)
    block_results = myconnect(sql2)
    pair_no = len(block_results)
    block_score = block_results[0][2]
    e_value = block_results[0][3]
    if pair_no>50: adj = 'huge'
    elif pair_no>10: adj = 'large'
    else: adj = 'small'
    data = "<hr />[%i] %s is contained in a %s %s block</a> (Score %s, <i>E</i>-value %s) with %s anchors<br />"%(si,get_details(lc),get_block_details(seg_id,lc,note),adj,block_score,e_value,pair_no)
    for datum in block_results:
        if lc in datum:
            if datum[4]==lc:
	        hit_col = 4
	        other_lc = datum[5]
	    else:
                hit_col = 5
                other_lc = datum[4]
                note_sp1, note_sp2 = note.split('_')
                note = note_sp2+'_'+note_sp1
	    break
    sql3 = """SELECT * from loci WHERE locus='%s'"""%(lc)
    sql4 = """SELECT * from loci WHERE locus='%s'"""%(other_lc)
    loci_results_a, loci_results_b = myconnect(sql3), myconnect(sql4)
    chr_a, center_a = loci_results_a[0][1],int(loci_results_a[0][2])
    chr_b, center_b = loci_results_b[0][1],int(loci_results_b[0][2])
    sp1, sp2 = note.split('_')
    segsize = sc
    start_a, stop_a, start_b, stop_b = center_a-segsize,center_a+segsize,center_b-segsize,center_b+segsize
    sql5 = """SELECT locus,chromo,end5,end3 from loci WHERE chromo='%s' AND end5 BETWEEN %i and %i AND sp='%s'"""%(chr_a,start_a, stop_a, sp1)
    sql6 = """SELECT locus,chromo,end5,end3 from loci WHERE chromo='%s' AND end5 BETWEEN %i and %i AND sp='%s'"""%(chr_b,start_b, stop_b, sp2)
    genelt_a, genelt_b = myconnect(sql5), myconnect(sql6)
    gene_name_lt_a = [x[0] for x in genelt_a]
    gene_name_lt_b = [x[0] for x in genelt_b]
    if hit_col==4: other_col=5
    else: other_col=4
    data+=segplot1(genelt_a,genelt_b,hit_col,block_results,lc,note,chr_a,chr_b,start_a,stop_a,start_b,stop_b)
    data += "<table class='stats'><tr class='hed'><td>Order within Block</td><td>Locus 1</td><td>Annotation 1</td><td>Locus 2</td><td>Annotation 2</td><td>Ka</td><td>Ks</td></tr>"
    j = 1
    for datum in block_results:
        d = datum[hit_col]
        if d in gene_name_lt_a and datum[other_col] in gene_name_lt_b:
	    if d==lc: datap="<tr class='acc'>"+''.join(["<td>%s</td>"]*7)+"</tr>"
            else: datap='<tr>'+''.join(['<td>%s</td>']*7)+'</tr>'
   	    ka,ks = '%.2f'%float(datum[8]),'%.2f'%float(datum[9])
            datap %= j,get_details(datum[4]),datum[10],get_details(datum[5]),datum[11],ka,ks
            data+=datap
        j+=1
    data += '</table><br />'
    return data

def get_external(lc, sp):
    fonttag = "<font color='red'> External Links </font> : "
    if sp=='Arabidopsis':
        return fonttag+"""<a href='http://www.tigr.org/tigr-scripts/euk_manatee/shared/ORF_infopage.cgi?db=ath1&amp;orf=%s'> TIGR </a> , <a href='http://mips.gsf.de/cgi-bin/proj/thal/search_gene?code=%s'> MIPS </a> , <a href='http://signal.salk.edu/cgi-bin/tdnaexpress?GENE=%s&amp;FUNCTION=&amp;TDNA=&amp;INTERVAL=50'> SALK </a> , <a href='http://arabidopsis.org/servlets/TairObject?type=locus&amp;name=%s'> TAIR </a>, <a href='http://www.floralgenome.org/tribedb/search.pl?action=keyword_results&type=id&term=%s'>PlantTribes</a>"""%(lc,lc,lc,lc,lc) 
    return fonttag + "<a href='http://genomevolution.com/CoGe/FeatView.pl?accn=%s'>CoGe</a>" % lc

def details1(req, lc):
    lc = lc.strip().capitalize()
    sql1 = """SELECT * from loci WHERE locus='%s'"""%(lc)
    results = myconnect(sql1)
    if results==-1: return DB_FAIL_MSG
    if len(results)==0: return "<font color='red'>We cannot find entries that contain %s.</font>"%lc
    # determine species
    prefix = lc[:2].lower()
    if prefix in sp_dict: sp = sp_dict[prefix]
    elif prefix=="": return "<font color='red'>Please enter a non-empty ID.</font>"
    else: sp = ""
    s = "<h1>Details for %s Locus %s</h1>"%(sp, lc)
    s1 = """
    <font color="red"> Position </font> : %s ( 5`- %s .. %s -3` )<br />
    <font color="red"> Annotation </font> : <font color="green">%s</font><br />
    %s
    <br /><br /><br />
    <font color="red"> Protein </font>[<a href='/duplication/index/blast_app/?id=%s&amp;seq=%s'>Map View</a>] <br />%s<br />
    <br /><br />
    <font color="red"> DNA </font><br />%s
    <br /><br /><br />
    """
    for datum in results:
        s+=s1%(datum[1],datum[2],datum[3],datum[4],get_external(lc,sp),lc,datum[5],format_seq(datum[5]),format_seq(datum[6]))
    return s+'<br /><br />'

def block_details1(req, seg_id, chr_low, chr_high, lc, note):
    if seg_id: sql2 = """SELECT * from block WHERE block_no='%s' AND note='%s' ORDER BY end5_1"""%(seg_id, note)
    if chr_low and chr_high: sql2 = """SELECT * from block WHERE chr_1=%s AND chr_2=%s AND note='%s' ORDER BY block_no, end5_1"""%(chr_low, chr_high, note)
    block_results = myconnect(sql2)
    if block_results==-1: return DB_FAIL_MSG
    data = ''
    header = "[%d] Block (Score %.1f, <i>E</i>-value %s) with %d anchors.<br /><table class='stats'><tr class='hed'><td>Order within Block</td><td>Locus 1</td><td>Annotation 1</td><td>Locus 2</td><td>Annotation 2</td><td>Ka</td><td>Ks</td></tr>"
    footer = "</table><hr />"
    seg_b4 = ''
    k = 0
    for datum in block_results:
        if datum[0]!=seg_b4:
            k += 1
            data+= footer
            data+= header%(k, datum[2], datum[3], datum[1])
            j=1
        if (not not lc) and (lc in datum): datap="<tr class='acc'>"+''.join(["<td>%s</td>"]*7)+"</tr>"
        else: datap="<tr>"+''.join(["<td>%s</td>"]*7)+"</tr>"
        ka,ks = '%.2f'%float(datum[8]),'%.2f'%float(datum[9])
        datap %= j,get_details(datum[4]),datum[10],get_details(datum[5]),datum[11],ka,ks
        j+=1
        data+=datap
        seg_b4 = datum[0]
    return data+footer+"<br />"+print_button

# check if one is close to border
def get_border(a3, a4, start_a, stop_a):
    tail, tip, flag = int(a3), int(a4), False
    if tail<start_a: tail=start_a;flag=True
    if tail>stop_a: tail=stop_a;flag=True
    if tip<start_a: tip=start_a;flag=True
    if tip>stop_a: tip=stop_a;flag=True
    return tail, tip, flag

def segplot1(genelt_a,genelt_b,hit_col,block_results,lc,species,chr_a,chr_b,start_a,stop_a,start_b,stop_b):

    fig, canvas, root = fig_init([8,2])
    # process input data
    genedt_b = {}
    # the other chromosome segment dictionary
    for t in genelt_b: genedt_b[t[0]]=(int(t[2]),int(t[3]))
    gene_name_lt_a = [x[0] for x in genelt_a]
    gene_name_lt_b = [x[0] for x in genelt_b]
    species_a, species_b = species.split('_')
    if hit_col==4: other_col=5
    else: other_col=4
    # chromosome segment start, stop in x-axis and y-axis
    st, sp = .04, .86
    mt, mp = .4, .75
    root.add_patch(Rectangle((st,mt),sp-st,.01,fc='g',ec='g'))
    root.add_patch(Rectangle((st,mp),sp-st,.01,fc='g',ec='g'))
    # break width, height
    bw, bh = .005, .01
    # broken chromosome on end
    root.plot([st-2*bw, st-bw],[mt-bh,mt+2*bh],'g-',lw=2)
    root.plot([st-bw, st],[mt-bh,mt+2*bh],'g-',lw=2)
    root.plot([st-2*bw, st-bw],[mp-bh,mp+2*bh],'g-',lw=2)
    root.plot([st-bw, st],[mp-bh,mp+2*bh],'g-',lw=2)
    root.plot([st-2*bw, st-bw],[mt-bh,mt+2*bh],'g-',lw=2)
    root.plot([st-bw, st],[mt-bh,mt+2*bh],'g-',lw=2)
    root.plot([st-2*bw, st-bw],[mp-bh,mp+2*bh],'g-',lw=2)
    root.plot([st-bw, st],[mp-bh,mp+2*bh],'g-',lw=2)
    # other end
    root.plot([sp+bw,sp+2*bw],[mt-bh,mt+2*bh],'g-',lw=2)
    root.plot([sp,sp+bw],[mt-bh,mt+2*bh],'g-',lw=2)
    root.plot([sp+bw,sp+2*bw],[mp-bh,mp+2*bh],'g-',lw=2)
    root.plot([sp,sp+bw],[mp-bh,mp+2*bh],'g-',lw=2)
    root.plot([sp+bw,sp+2*bw],[mt-bh,mt+2*bh],'g-',lw=2)
    root.plot([sp,sp+bw],[mt-bh,mt+2*bh],'g-',lw=2)
    root.plot([sp+bw,sp+2*bw],[mp-bh,mp+2*bh],'g-',lw=2)
    root.plot([sp,sp+bw],[mp-bh,mp+2*bh],'g-',lw=2)
    # chromosome names
    root.text(sp+bw*3,mp,'%s %s'%(species_a.capitalize(),chr_a),color='r')
    root.text(sp+bw*3,mt,'%s %s'%(species_b.capitalize(),chr_b),color='r')
    # species names
    root.text(sp+bw*3,mp+.15,sp_dict[species_a.lower()],va="center",fontweight="bold",color="k")
    root.text(sp+bw*3,mt-.15,sp_dict[species_b.lower()],va="center",fontweight="bold",color="k")
    # physical position
    root.text(sp+bw*3,mp-.07,'%.2f-%.2fMb'%(start_a/1000000.,stop_a/1000000.),size=8)
    root.text(sp+bw*3,mt-.07,'%.2f-%.2fMb'%(start_b/1000000.,stop_b/1000000.),size=8)
        
    scale = 1.*(sp-st)/(stop_a-start_a)
    for b in genelt_b:
        tail_b, tip_b, flag_b = get_border(b[2],b[3],start_b,stop_b)
        if flag_b: arrow_b = Rectangle(((tail_b-start_b)*scale+st,mt-.015),(tip_b-tail_b)*scale,.03)
        else: arrow_b = Arrow((tail_b-start_b)*scale+st,mt,(tip_b-tail_b)*scale,0,width=.15)
        setp(arrow_b, fc='w', ec='k', lw=1)
        root.add_patch(arrow_b)
    for a in genelt_a:
    	tail_a, tip_a, flag_a = get_border(a[2],a[3],start_a,stop_a)
    	tail_aa, tip_aa = (tail_a-start_a)*scale+st, (tip_a-start_a)*scale+st
        if flag_a: arrow_a = Rectangle((tail_aa,mp-.015),tip_aa-tail_aa,.03)
        else: arrow_a = Arrow(tail_aa,mp,tip_aa-tail_aa,0,width=.15)
        setp(arrow_a, fc='w', ec='k', lw=1)
        for datum in block_results:
            if a[0]!=datum[hit_col] or datum[other_col] not in genedt_b: continue
            center_a = (tail_aa+tip_aa)/2
            b = genedt_b[datum[other_col]]
            tail_b, tip_b, flag_b = get_border(b[0],b[1],start_b,stop_b)
            tail_bb, tip_bb = (tail_b-start_b)*scale+st, (tip_b-start_b)*scale+st
            center_b = (tail_bb+tip_bb)/2
            # anchor labels
            cc = 'b'
            if a[0]==lc:
                cc = 'r'
                # highlight the match
                root.add_patch(Polygon([[tail_aa, mp-.06],[tip_aa, mp-.06],[tip_bb, mt+.06],[tail_bb, mt+.06]], fc="gold", ec="gold", alpha=.5))
            root.text(center_a,mp+.06,a[0][-5:],rotation=45,color=cc,size=7,horizontalalignment='center')
            root.text(center_b,mt-.18,datum[other_col][-5:],rotation=45,color=cc,size=7,horizontalalignment='center')
            # connect syntenic lines
            root.plot([center_a,center_b],[mp-.06,mt+.06],'bo-',lw=1,mec='b',mew=1,mfc='w',ms=4)
            if a[0]==lc:
                root.plot([center_a,center_b],[mp-.06,mt+.06],'ro-',lw=1,mec='r',mew=1,mfc='w',ms=4)
            if flag_b: arrow_b = Rectangle((tail_bb,mt-.015),tip_bb-tail_bb,.03)
            else: arrow_b = Arrow(tail_bb,mt,tip_bb-tail_bb,0,width=.15)
            setp(arrow_a, fc=cc, ec='k', lw=1)
            setp(arrow_b, fc=cc, ec='k', lw=1)
        root.add_patch(arrow_a)
        root.add_patch(arrow_b)

    fa, fi = fig_terminate(root, canvas)
    img_location = "/duplication/scripts/to_pdf?imagename=%s" % fa
    return "<img class='articleimg' alt='' src='/duplication/usr/%s' />" % fi + \
           "<img src='/duplication/images/icons/pdf.png' alt='Export to pdf' " + \
           "onclick=\"window.location.href='%s'\" />" % img_location 
