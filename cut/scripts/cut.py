import os
import os.path as op
import json
import traceback
import StringIO

from subprocess import Popen, PIPE
from random import randint


# Generator to buffer file chunks
def fbuffer(f, chunk_size=10000):
   while True:
      chunk = f.read(chunk_size)
      if not chunk: break
      yield chunk


def write_to_file(str=None):
    fname = "tmp_%05d" % randint(0, 100000)
    fname = "/var/www/duplication/usr/" + fname
    if str:
        f = open(fname, "wb", 10000)
        f.write(str)
	f.close()
    return fname

# wrap the linux line feed and then convert to breaks
line_feed = lambda stream: stream.split('\n') if stream else ""
remove_quote = lambda s: s.replace('\'','').replace('\"','')


def index(req):
    #return json.dumps(handle(req))
    try:
        json_out = handle(req)
    except:
        tb = StringIO.StringIO()
        traceback.print_exc(file=tb)
        json_out = dict(out_f="", cmd="", stdout_str="", stderr_str=tb.read())

    return json.dumps(json_out)


def handle(req):

    tree_str = req.form.get('tree', '').strip()
    list_str = req.form.get('list', '').strip()
    tree_str, list_str = remove_quote(tree_str), remove_quote(list_str)
    pvalue = req.form.get('pvalue', ".01")

    tree_f = write_to_file(tree_str) 
    list_f = write_to_file(list_str)

    out_f = write_to_file() + ".png"
    cmd = "MPLCONFIGDIR=/var/www/duplication/usr/ /usr/bin/python " + \
            "/var/www/duplication/apps/treecut/treecut.py " + \
            "--cutoff %s %s %s %s" % (pvalue, tree_f, list_f, out_f)

    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)

    stdout, stderr = p.communicate() 
    stdout_str = line_feed(stdout)
    stderr_str = line_feed(stderr)

    # cleanup
    for f in (tree_f, list_f): 
        if op.exists(f): os.remove(f)

    out_f = out_f.replace("/var/www", "")
    json_out = dict(out_f=out_f, cmd=cmd, stdout_str=stdout_str, stderr_str=stderr_str)

    return json_out

