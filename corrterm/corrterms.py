# FILE: corrterms.py

from graph_quad import *
from seifert import s_quad_form, parse_seifert, correct_form
from ndqf import NDQF
import traceback

'''
Command line usage for double branched cover and Seifert data
OR     python corrterms.py [-k] [-m] archive_num
OR     python corrterms.py -kf [-m] archive_num.txt
OR     python corrterms.py -p [-m] [filename]
OR     python corrterms.py -s [-m] '[e, (p1, q1),...,(pr, qr)]'

[-k] to download and save Knotilus archive_num plaintext to archive_num.txt
-kf to load archive_num.txt (Knotilus plaintext file)
-p to use Plink, [filename] to load file
-s to use Seifert data
[-m] to use multiprocessing
'''

def seifert_corr(stringdata, use_multi=False):
    '''Parse Seifert data, output correction terms.'''
    try:
        if stringdata == '':
            raise ValueError('empty string')
        data = parse_seifert(stringdata) # parse data
    except:
        print traceback.print_exc()            
        return
    if not correct_form(data, gui=False):
        print traceback.print_exc()
        return
    else:
        # compute quadratic form and correction terms
        quad = s_quad_form(data)
        print quad
        quadform = NDQF(quad[0])
        print 'H_1(Y) ~ %s' % quadform.group.struct()        
        if use_multi:
            corr = quadform.correction_terms_threaded()
        else:
            corr = quadform.correction_terms_ugly()
        if quad[1]: # reversed orientation
            corr = map(lambda n: -n, corr)
        corr = quadform.pretty_print(corr) # make Fractions pretty
    return corr

def main(loading_type, loading_data=None, use_multi=False):
    '''
    Return Heegaard Floer correction terms.
    
    loading_type - 'k' for Knotilus, 'p' for PLink, 's' for Seifert
    loading_data - Knotilus archive number, filename, Seifert data
    multi - use multiprocessing or not
    '''
    print '\n%s' %loading_data
    if loading_type == 'p': # PLink
        if loading_data:
            print 'Loading PLink'
            data = load_plink(loading_data)
        else:
            print 'Loading new PLink'
            data = load_plink()
        all_data = make_objects(data[0],data[1],data[2],data[3],data[4],data[5])            
        regions = all_data[3]
    elif loading_type == '': # Knotilus download
        print 'Downloading from Knotilus'
        regions = load(loading_data, False, False)[3]
    elif loading_type == 'k': # Knotilus download and save
        print 'Downloading and saving from Knotilus'
        regions = load(loading_data, False, True)[3]
    elif loading_type == 'kf': # Knotilus load file
        print 'Loading Knotilus file'
        regions = load(loading_data, True, False)[3]
    elif loading_type == 's':
        print 'Seifert data'
    else:
        usage()
    # compute correction terms
    if loading_type != 's':
        if regions: # non-empty (i.e. not unknot with no crossings)         
            nodes = [NodeClass(i) for i in range(len(regions))]
            tree = edges_regions(nodes,regions)
            max_subtree = maximal_subtree(tree, nodes)
            minus = minus_maximal_subtree(tree, max_subtree)
            quad = quad_form(tree, minus, nodes)
            print quad
            quadform = NDQF(quad)
            corr = quadform.correction_terms(use_multi)
        else: # unknot with no crossings
            print 'quadratic form N/A (unknot with no crossings)'
            print 'H_1(Y) ~ 1'
            print '0' # corrterms - only 1 spin structure
    else: # Seifert
        corr = seifert_corr(loading_data, use_multi)
        print corr
    return
        
def usage():
    print 'OR     python corrterms.py [-k] [-m] archive_num'
    print 'OR     python corrterms.py -kf [-m] archive_num.txt'
    print 'OR     python corrterms.py -p [-m] [filename]'
    print "OR     python corrterms.py -s [-m] '[e, (p1, q1),...,(pr, qr)]'"
    sys.exit(1)  
    
if __name__ == '__main__':
    mainvars = ['', None, False] # loading_type, data, multi
    if len(sys.argv) == 1:
        usage()
    try:
        for arg in sys.argv[1:]:
            # Handle options
            if arg[0] == '-':
                if arg == '-m': # multiprocessing
                    mainvars[2] = True
                else:
                    if not mainvars[0]: # loading type
                        mainvars[0] = arg[1:]
                    elif mainvars[0] != arg[1:]:
                        usage()
            # Handle loading data
            else:
                if not mainvars[1]: # loading data
                    mainvars[1] = arg
                else: # loading data already specified
                    usage()
        main(mainvars[0], mainvars[1], mainvars[2])
    except Exception:
        print '\nERROR: ABORTING PROGRAM'
        print traceback.format_exc()
        print '%s\n' %traceback.format_exc().splitlines()[-1]
        usage()