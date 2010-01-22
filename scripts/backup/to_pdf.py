import os
from reportlab.graphics.shapes import Image, Drawing
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import LETTER, inch
from glob import glob

def index(req, imagename):
    IMAGES = []
    imagelist = map(lambda x:'/var/www/duplication/usr/%s.png'%x, [imagename])
    for inPath in imagelist:
        img = Image(.6*inch, LETTER[1]/2.0-(LETTER[0]-1.2*inch)/2.0, LETTER[0]-1.2*inch, LETTER[0]-1.2*inch, inPath)
        IMAGES.append(img)

    id = 0
    for img in IMAGES:
        id+=1
        d = Drawing(LETTER[0], LETTER[1])
        d.add(img)
        outPath = img.path.split('.')[0]+'.pdf'
        renderPDF.drawToFile(d, outPath)
    req.header='Content-type: application/pdf'
    req.set_content_length(os.path.getsize(outPath))
    req.headers_out["Content-Disposition"]="attachment;filename=output.pdf"
    req.sendfile(outPath)
