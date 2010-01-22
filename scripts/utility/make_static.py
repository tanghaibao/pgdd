#!/usr/bin/python
from urllib import urlretrieve
from glob import glob
htm_list = glob('/var/www/duplication/templates/*_body.htm')
for h in htm_list:
	s = h.split('/')[-1].split('_')[0]
	if s=='home': s='index'
	print s
	urlretrieve('http://chibba.agtec.uga.edu/duplication/index/%s'%s, '/var/www/duplication/%s.htm'%s)
