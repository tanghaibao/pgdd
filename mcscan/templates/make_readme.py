#!/usr/bin/python

readme = file("README").read()
fw = file("readme_template.htm",'w')
readme = readme.replace('\n', "<br />")
fw.write("<font name='Courier New'>\n%s\n</font>"%readme)
fw.close()
