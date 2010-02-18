import os

def index(req, imagename):

    outPath = "/var/www/duplication/usr/%s.pdf" % imagename 

    req.header='Content-type: application/pdf'
    req.set_content_length(os.path.getsize(outPath))
    req.headers_out["Content-Disposition"]="attachment;filename=output.pdf"
    req.sendfile(outPath)
