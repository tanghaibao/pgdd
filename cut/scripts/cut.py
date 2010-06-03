import os
import os.path as op
from random import randint


# Generator to buffer file chunks
def fbuffer(f, chunk_size=10000):
   while True:
      chunk = f.read(chunk_size)
      if not chunk: break
      yield chunk


def write_to_file(str):
    fname = "tmp_%05d" % randint(0, 100000)
    fname = "/var/www/duplication/usr/" + fname
    if str:
        f = open(fname, "wb", 10000)
        f.write(str)
	f.close()
    return fname


def index(req):

    tree_str = req.form['tree']
    list_str = req.form['list']

    if tree_str:
        tree_f = write_to_file(tree_str) 
    if list_str:
        list_f = write_to_file(list_str)

    out_f = write_to_file(None) + ".png"
    cmd = "/usr/bin/python /var/www/duplication/apps/treecut/treecut.py %s %s %s" % (tree_f, list_f, out_f)

    stdin, stdout, stderr = os.popen3(cmd)
    stdout_str, stderr_str = stdout.read(), stderr.read()
    #return "Cmd:%s\nOut:\n%s\nError:\n%s" % (cmd, stdout_str, stderr_str) 

    # cleanup
    for f in (tree_f, list_f): 
        if op.exists(f): os.remove(f)

    out_f = out_f.replace("/var/www", "")
    return out_f

