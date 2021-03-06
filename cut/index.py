import os
import sys
import string
import imp
import stat
from mod_python import psp
os.environ['HOME']='/var/www/duplication/usr/'

# subdirectory where we place templates
_TMPL_DIR = "templates"
# the name for the "shell" template
_MAIN_TMPL = "main_frame.htm"

# mod_python module reload function
def import_module(module_name, req=None, path=['/var/www/duplication/scripts/']):
    """
    Get the module to handle the request. If
    autoreload is on, then the module will be reloaded
    if it has changed since the last import.
    """
    # get the options
    autoreload, debug = 1, None
    if req:
        config = req.get_config()
        autoreload = not config.has_key("PythonNoReload")
        debug = not config.has_key("PythonDebug")
    # try to import the module
    oldmtime = None
    mtime = None
    if not autoreload:
        parts = string.split(module_name, '.')
        for i in range(len(parts)):
            f, p, d = imp.find_module(parts[i], path)
            try:
                mname = string.join(parts[:i+1], ".")
                module = imp.load_module(mname, f, p, d)
            finally:
                #if f: f.close()
		return parts[i],module_name
            if hasattr(module, "__path__"):
                path = module.__path__
    else:
        # keep track of file modification time and
        # try to reload it if it is newer
        if sys.modules.has_key(module_name):
            # the we won't even bother importing
            module = sys.modules[module_name]
            # does it have __mtime__ ?
            if sys.modules[module_name].__dict__.has_key("__mtime__"):
                # remember it
                oldmtime = sys.modules[ module_name ].__mtime__
        # import the module for the first time
        else:
            parts = string.split(module_name, '.')
            for i in range(len(parts)):
                f, p, d = imp.find_module(parts[i], path)
                try:
                    mname = string.join(parts[:i+1], ".")
                    module = imp.load_module(mname, f, p, d)
                finally:
                    if f: f.close()
                if hasattr(module, "__path__"):
                    path = module.__path__
        # find out the last modification time
        # but only if there is a __file__ attr
        if module.__dict__.has_key("__file__"):
            filepath = module.__file__
            if os.path.exists(filepath):
                mod = os.stat(filepath)
                mtime = mod[stat.ST_MTIME]
            # check also .py and take the newest
            if os.path.exists(filepath[:-1]) :
                # get the time of the .py file
                mod = os.stat(filepath[:-1])
                mtime = max(mtime, mod[stat.ST_MTIME])
    # if module is newer - reload
    if (autoreload and (oldmtime < mtime)):
        del sys.modules[module_name]
        # import the module as if for the first time
        parts = string.split(module_name, '.')
        for i in range(len(parts)):
            f, p, d = imp.find_module(parts[i], path)
            try:
                mname = string.join(parts[:i+1], ".")
                module = imp.load_module(mname, f, p, d)
            finally:
                if f: f.close()
            if hasattr(module, "__path__"):
                path = module.__path__
    # save mtime
    module.__mtime__ = mtime

    return module

##
# External functions. These can be accessed via URL's from
# outside.
def index(req):
    # The publisher will call this function as default,
    # make it same as home
    return home(req)

def home(req):
    return _page(req, 'home')

def results(req):
    return _page(req, 'results')

##
# Internal functions. Because they begin with an underscore,
# the publisher will not allow them to be accessible from the
# web. Perhaps a cleaner technique is to place these into a
# seprate module. If that module contains __access__ = 0 global
# variable, then none of its contents would be accessible via
# the publisher, in which case you don't need to prepend
# underscores to function names.

def _base_url(req, ssl=0):
    """
    This function makes its best effort to guess the base url.
    Sometimes it is simpler to just hard code the base url as
    a constant, but doing something like this makes the application
    independent of what the name of the site is.
    """
    
    # first choice is the 'Host' header, second is the
    # hostname in the Apache server configuration.
    host = req.headers_in.get('host', req.server.server_hostname)
    
    # are we running on an unusual port?
    if not ':' in host:
        port = req.connection.local_addr[1]
        if port != 80 and not ssl:
            host = "%s:%d" % (host, req.connection.local_addr[1])

    # SSL?        
    if ssl:
        base = 'https://' + host + req.uri
    else:
        base = 'http://' + host + req.uri

    # chop off the last part of the URL    
    return os.path.split(base)[0]

def _tmpl_path(name):
    """ A shorthand for building a full path to a template """
    return os.path.join(_TMPL_DIR, name)

def _page(req, name):
    """
    Construct a web page given a page name, which is a string identifier
    that is also passed to the _menu() function to highlight the current
    menu item, and is used to construct the filename for the page template.
    """

    body_tmpl = _tmpl_path('%s_body.htm' % name)
    vars = {"body": psp.PSP(req, body_tmpl)}

    return psp.PSP(req, _tmpl_path(_MAIN_TMPL), vars=vars)

