import cgi

def fill():
   s = """\
<html><body>
<form method="get" action="./show">
<p>Type a word: <input type="text" name="word">
<input type="submit" value="Submit"</p>
</form></body></html>
"""
   return s

# Receive the Request object
def show(req):
   # The getfirst() method returns the value of the first field with the
   # name passed as the method argument
   word = req.form.getfirst('word', '')

   # Escape the user input to avoid script injection attacks
   word = cgi.escape(word)

   s = """\
<html><body>
<p>The submitted word was "%s"</p>
<p><a href="./fill">Submit another word!</a></p>
</body></html>
"""
   return s % word