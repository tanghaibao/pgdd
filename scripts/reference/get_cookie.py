from mod_python import Cookie
import time

def index(req):

   # Retrieve a dictionary like object containing all cookies
   all_cookies = Cookie.get_cookies(req)

   # Get the last_visit cookie
   last_visit = all_cookies.get('last_visit', None)

   # If the last_visit cookie exists show last visit
   if last_visit:
      message = 'Your last visit was at %s'
      message %= time.asctime(time.localtime(float(last_visit.value)))
   else:
      message = 'This is your first visit'
      
   c = Cookie.Cookie('last_visit', time.time())

   # The cookie will expire in 30 days.
   c.expires = time.time() + 30 * 24 * 60 * 60

   # Add the cookie to the HTTP header.
   Cookie.add_cookie(req, c)

   return """\
<html><body>
<p>%s</p>
<p><pre>%s</pre></p>
<p>%s</p>
</body></html>
""" % ('You have just received this cookie:', c, message)