import cgi
import os
from tempfile import mkstemp

def blast1(req):
    """blast commandline to run blastall with three use-input params
    """
    database = "at_mt_oy_pa_po_sb_vv"
    seq = req.form.getfirst('seq')
    id = req.form.getfirst('id')
    filter = req.form.getfirst('filter')
    evalue = req.form.getfirst('evalue')
    program = req.form.getfirst('program')
    # default value
    if not program: program="blastp"
    if not filter: filter="T"
    if not evalue: evalue="1e-5"
    tmp_fd, tmp_fn = mkstemp()
    fw = os.fdopen(tmp_fd, "w")
    if seq.startswith(">"): fw.write(seq)
    elif id: fw.write(">%s\n%s"%(id, seq))
    else: fw.write(">%s\n%s"%("usr_seq",seq))
    fw.close()
    # run blastall command
    res = os.popen("blastall -i %s -d /var/www/duplication/data/%s -e %s -T T -p %s -F %s"%(tmp_fn, database, evalue, program, filter)).read()
    os.remove(tmp_fn)
    return "<hr />"+res
