#!/usr/bin/python
import os
os.system('cp -r /var/www/duplication/css/ /home/bao/apache/')
print 'backup css'
os.system('cp -r /var/www/duplication/scripts/ /home/bao/apache/')
print 'backup scripts'
os.system('cp -r /var/www/duplication/templates/ /home/bao/apache/')
print 'backup templates'
os.system('cp -r /var/www/duplication/data/*.py /home/bao/apache/data/')
print 'backup data/*.py'
os.system('cp /var/www/duplication/index.py /home/bao/apache/')
print 'backup index.py'
