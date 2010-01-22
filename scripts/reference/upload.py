import os

def form():
   return """\
<html><body>
<form enctype="multipart/form-data" action="./upload" method="post">
<p>File: <input type="file" name="file"></p>
<p><input type="submit" value="Upload"></p>
</form>
</body></html>
"""

# Generator to buffer file chunks
def fbuffer(f, chunk_size=10000):
   while True:
      chunk = f.read(chunk_size)
      if not chunk: break
      yield chunk

def upload(req):
   
   try: # Windows needs stdio set for binary mode.
      import msvcrt
      msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
      msvcrt.setmode (1, os.O_BINARY) # stdout = 1
   except ImportError:
      pass

   # A nested FieldStorage instance holds the file
   fileitem = req.form['file']

   # Test if the file was uploaded
   if fileitem.filename:

      # strip leading path from file name to avoid directory traversal attacks
      fname = os.path.basename(fileitem.filename)
      # build absolute path to files directory
      dir_path = os.path.join(os.path.dirname(req.filename), 'files')
      f = open(os.path.join(dir_path, fname), 'wb', 10000)

      # Read the file in chunks
      for chunk in fbuffer(fileitem.file):
         f.write(chunk)
      f.close()
      message = 'The file "%s" was uploaded successfully' % fname

   else:
      message = 'No file was uploaded'
   
   return """\
<html><body>
<p>%s</p>
<p><a href="./form">Upload another file</a></p>
</body></html>
""" % message