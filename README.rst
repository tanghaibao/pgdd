.. image:: http://chibba.agtec.uga.edu/duplication/images/icons/PGDD.png 
    :alt: pgdd

Server scripts in PGDD
===========================
This package includes most of the server contents on `Plant genome duplication database <http://chibba.agtec.uga.edu/duplication>`_ (except the database connector script for security reasons). Contains ``scripts``, ``templates``, ``css`` and ``images`` folder.


Installation
=============
- Apache configuration. `mod_python <http://www.modpython.org/>`__ is required for this to run on your server. You might also need to change ``apache2.conf`` to allow ``mod_python.publisher`` to treat your scripts as python scripts::

    ## For Bao's mod_python stuff

    <Directory "/var/www/duplication/">
        AddHandler mod_python .py
        PythonHandler mod_python.publisher
        PythonDebug On
    </Directory>

    <Directory "/var/www/duplication/scripts/">
        AddHandler mod_python .py
        PythonHandler mod_python.publisher
        PythonDebug On
    </Directory>

    <Directory "/var/www/duplication/images/">
        SetHandler None
    </Directory>

    <Directory "/var/www/duplication/css/">
        SetHandler None
    </Directory>

- MySQL databases. Look at the database connector script in ``scripts/preferences.py``. The default database name is ``bao`` and two tables ``loci`` and ``block`` with the schema documented `here <http://chibba.agtec.uga.edu/duplication/wiki/index.php/PGDD_documentation>`__.
