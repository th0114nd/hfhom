# FILE: corrterms.py

from graph_quad import *
from seifert import s_quad_form
from ndqf import NDQF

'''
Command line usage for double branched cover and Seifert data
usage: python corrterms.py [-d] archive_num
OR     python corrterms.py -f archive_num.txt
OR     python corrterms.py -p [filename]
OR     python corrterms.py -s [e, (p1, q1),...,(pr, qr)]

[-d] to download and save Knotilus archive_num plaintext to archive_num.txt
-f to load archive_num.txt (Knotilus plaintext file)
-p to use Plink, [filename] to load file
-s to use Seifert data
'''

def seifert(data):
    '''Parse Seifert data.'''
    try:
        # parse data            
        stringdata = stringdata.replace(' ','') # remove all spaces
        data = []
        stringdata = stringdata.split('[')[1].split(']')[0] # remove [, ]
        stringdata = stringdata.split(',(')
        data.append(int(stringdata[0])) # append e
        for pair in stringdata[1:]:
            pairlist = pair.split(',')
            pairlist[0] = int(pairlist[0])
            pairlist[1] = int(pairlist[1][:-1]) # ignore last ')'
            data.append(tuple(pairlist))
    except:
        tkMessageBox.showwarning('Failed to parse data.',
                'Data should be [e, (p1,q1), (p2,q2), ... , (pr,qr)],' +\
                'where e and the pi,qi are ints, pi > 1, and gcd(pi,qi) ' +\
                '= 1.')
        print traceback.print_exc()            
        return
    if not correct_form(data, gui=True):
        tkMessageBox.showwarning('Invalid data form.',
                'Data should be [e, (p1,q1), (p2,q2), ... , (pr,qr)],' +\
                'where e and the pi,qi are ints, pi > 1, and gcd(pi,qi) ' +\
                '= 1.')
        print traceback.print_exc()
        return
    else:
        quad = s_quad_form(data)
        print quad
        quadform = NDQF(quad[0])
        corr = quadform.correction_terms_ugly()
        print quadform.group.struct()
        if quad[1]: # reversed orientation
            corr = map(lambda n: -n, corr)
        return quadform.pretty_print(corr) # make Fractions pretty

def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == '-p': # Plink
            data = load_plink()
            all_data = make_objects(data[0],data[1],data[2],data[3],data[4],\
                                    data[5])            
            regions = all_data[3]
        else:
            regions = load(sys.argv[1], False, False)[3] # knotilus
    elif len(sys.argv) == 3:
        if sys.argv[1] == '-f':
            regions = load(sys.argv[2], True, False)[3]
        elif sys.argv[1] == '-s':
            regions = load(sys.argv[2], False, True)[3]
        elif sys.argv[1] == '-p': # Plink
            data = load_plink(sys.argv[2])
            all_data = make_objects(data[0],data[1],data[2],data[3],data[4],\
                                    data[5])           
            regions = all_data[3]
    else:
        usage()

    
if __name__ == '__main__':
    main()