import os

def index(req):
    req.content_type = "text/html"

    req.add_common_vars()
    env_vars = req.subprocess_env.copy()
    from re import search
    keys = os.environ.keys()
    for key in keys:
        if not search('HOME',key):
            os.environ["HOME"]="/var/www/duplication/usr/"
    s = ''

    s +='<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
    s +='<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">'
    s +='<head><title>mod_python.publisher</title></head>'
    s +='<body>'
    s +='<h1>Environment Variables</h1>'
    s +='<table border="1">'
    keys = os.environ.keys()
    for key in keys:
        s +='<tr><td>%s</td><td>%s</td></tr>' % (key, os.environ[key])
    s +='</table>'
    s +='</body>'
    s +='</html>'
    return s

