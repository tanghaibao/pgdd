# see http://return-true.com/2009/08/how-to-jquery-autocomplete/

from preferences import myconnect
import json

def index(req):
    q = req.form.getfirst("term")
    query = "SELECT locus FROM loci WHERE locus LIKE '%s%%' ORDER by locus limit 5" % q
    res = myconnect(query)
    return json.dumps([x[0] for x in res])

