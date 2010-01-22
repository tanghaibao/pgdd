import os
from urllib import urlretrieve

def parse(req, referer):
    fn = "/var/www/duplication/usr/"+referer.split('/')[-1]
    urlretrieve(referer, fn)
    out = os.popen('/var/www/duplication/apps/code2html %s'%fn).read()
    if out=='': return file(fn).read()
    else: return out
