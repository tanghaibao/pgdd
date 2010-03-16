from preferences import myconnect, DB_FAIL_MSG
import os

def index(req):

    try:
        species1 = req.form.getfirst('sp1')
        species2 = req.form.getfirst('sp2')
    except:
        return "<font color='red'>Please select species from both lists.</font>"

    if species1 > species2:
        species1, species2 = species2, species1

    header = "block_no,block_score,e_value,locus_1,locus_2,ka,ks"
    sql1 = "SELECT %s from block WHERE note='%s_%s' AND chr_1 is not NULL AND chr_2 is not NULL" % (header, species1, species2)
    results = myconnect(sql1)
    if results==-1: return DB_FAIL_MSG

    # write to intermediate file
    os.chdir("/var/www/duplication/usr/")
    file_name = "%s_%s_block.csv.gz" % (species1, species2)

    if not os.path.exists(file_name):
        import gzip 
        f = gzip.open(file_name, "wb")
        f.write(header + "\n")
        for r in results:
            f.write(",".join(str(x) for x in r) + "\n")
        f.close()

    return "%d records found. Transferring data ..." % len(results)
    
