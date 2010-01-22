import cgi

def fill():
   s = """\
<html><body>
<form method="post" action="./show">
Red<input type="checkbox" name="color" value="red">
Green<input type="checkbox" name="color" value="green">
Blue<input type="checkbox" name="color" value="blue">
<input type="submit" value="Submit">
</form>
</body></html>
"""
   return s

# Receive the Request object
def show(req):
   # The getlist() method returns a list with all the values of 
   # the fields named as the method argument
   colors = req.form.getlist('color')

   # Escape the user input to avoid script injection attacks
   colors = map(lambda color: cgi.escape(color), colors)

   s = """\
<html><body>
<p>The submitted colors were "%s"</p>
<p><a href="./fill">Submit again!</a></p>
</body></html>
"""
   return s % ', '.join(colors)