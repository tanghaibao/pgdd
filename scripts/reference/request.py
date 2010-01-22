from cgi import escape
from urllib import unquote

# The Publisher passes the Request object to the function
def index(req):
   s = """\
<html><head>
<style type="text/css">
td {padding:0.2em 0.5em;border:1px solid black;}
table {border-collapse:collapse;}
</style>
</head><body>
<table cellspacing="0" cellpadding="0">%s</table>
</body></html>
"""
   attribs = ''

   # Loop over the Request object attributes
   for attrib in dir(req):
      attribs += '<tr><td>%s</td><td>%s</td></tr>'
      attribs %= (attrib, escape(unquote(str(req.__getattribute__(attrib)))))

   return s % (attribs)