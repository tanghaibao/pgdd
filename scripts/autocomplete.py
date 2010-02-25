# see http://return-true.com/2009/08/how-to-jquery-autocomplete/

from preferences import myconnect

def index(req):
    q = req.form.getfirst("q")
    query = "SELECT locus FROM loci WHERE locus LIKE '%s%%' ORDER by locus limit 5" % q
    res = myconnect(query)
    out = "\n".join(x[0] for x in res)
    return out
