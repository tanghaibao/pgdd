from mod_python import Cookie
import time

def index(req):

   # Create a cookie object named last_visit
   # with the value of the server's current UTC time
   c = Cookie.Cookie('last_visit', time.time())

   # The cookie will expire in 30 days.
   c.expires = time.time() + 30 * 24 * 60 * 60

   # Add the cookie to the HTTP header.
   Cookie.add_cookie(req, c)

   return """\
<html><body>
<p>%s</p>
<p>%s</p>
</body></html>
""" % ('You have just received this cookie:', c)