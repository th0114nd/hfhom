# Caltech SURF 2013
# FILE: knotilus_download.py
# AUTHOR: Laura Shou
# MENTOR: Professor Yi Ni
# 07.08.13

import sys
import cStringIO
import time
import urllib2

'''
This module downloads the plaintext file corresponding to a link from the 
Knotilus database. (http://knotilus.math.uwo.ca/)
It supports using the Knotilus archive number to look up and download the 
plaintext file.

usage: python knotilus_download [-s] archive_num
       - optional arg [-s] to save link data to file 'archive_num.txt' and 
         suppress output
       - otherwise print the plaintext file for archive_num
'''

class KURLError(Exception): # Knotilus URL Error
    pass

def valid_archive_form(archive):
    '''
    Given a string 'archive', returns 'True' if 'archive' is of the form
    ax-b-c for ints a,b,c and character 'x', and 'False' otherwise.
    '''
    try:
        xpos = archive.find('x-')
        a = int(archive[0:xpos]) # make sure a is an int
        last = archive.rfind('-')
        b = int(archive[xpos+2:last]) # make sure b is an int
        c = int(archive[last:]) # make sure c is an int  
    except:
        return False
    return True

def get_page_source(url):
    '''
    Returns the page source (string) of url.
    '''
    print 'Getting page source......',  
    page = urllib2.urlopen(url)
    page_source = page.read()
    print '[DONE]'
    page.close()
    return page_source

def gauss_code(archive):
    '''
    Given an archive number, gets the page source, then finds and returns
    the Knotilus Gauss code as a string, of the form 
    '&knot=(gauss_code_1)&std=(gauss_code_2)'
    
    gauss_code_1 and gauss_code_2 are possibly different (but describe the same
    link, up to mirroring or starting at a different location). For an example
    of this, look up 7x-1-1. The gauss_code_2 is the essential Gauss code for
    downloading files.
    '''
    # make sure archive is in the correct from ax-b-c for ints a,b,c
    if not valid_archive_form(archive):
        raise KURLError('archive num must be of form ax-b-c, for a,b,c ints')
    
    url = 'http://knotilus.math.uwo.ca/draw.php?archive=%s&javadraw=off'%archive
    page_source = get_page_source(url)
    source = cStringIO.StringIO(page_source) # treat string like a file
    valid = False # whether the url is valid or not

    # find the Gauss code!
    for line in source:
        if '&knot=' in line: # this is the line with the Gauss code
            correct_line = line
            valid = True # valid url
            break
    if valid == False: # didn't find the Gauss code
        raise KURLError('not a valid archive number')
    
    text = correct_line.split()
    for item in text: # isolate the part of the line that has the gauss code
        if '&knot=' in item:
            gauss = item
            break
    gauss = gauss[1:-1] # remove " marks at start and end
    # gauss is of the form '&knot=1,2,3,4:1,2,3,4&std=1,2,3,4:1,2,3,4'
    return gauss

def get_plaintext(archive, max_attempts=12):
    '''
    Given the archive number code, returns the plaintext file download from 
    Knotilus.
    
    max_attempts = number of tries before aborting loading
    '''
    # form the URL
    # http://knotilus.math.uwo.ca/dl.php?r=0&m=0&a=0&i=0&ext=-1
    # &knot=(gauss code)&std=(gauss code)
    # &type=txt
    gauss = gauss_code(archive)
    url= 'http://knotilus.math.uwo.ca/dl.php?r=0&m=0&a=0&i=0&ext=-1%s&type=txt'\
        % gauss
    plaintext = get_page_source(url)
    
    start = time.time()
    for i in range(max_attempts):
        if plaintext != '': # loaded/annealed completely
            break
        # not loaded/annealed completely => keep refreshing url_load to load it
        url_load = 'http://knotilus.math.uwo.ca/show.php?' + \
            'id=1&%s&ext=-1&r=0&m=0&a=0&i=0' % gauss
        page = urllib2.urlopen(url_load)
        print 'Annealing...'
        time.sleep(1.5) # 1.5 seconds seems around the best waiting time
        plaintext = get_page_source(url)        
        page.close()
    print 'took %g sec to anneal' % (time.time() - start)
    return plaintext

# this is a silly function for fun :P
# you should kill it at some time; it's never gonna reach 98 billion any time
# soon ;P
# if running in the terminal, kill it with Ctrl + \
def everything(start_archive):
    '''
    Check which archive numbers are valid...???
    '''
    for num_crossings in range(2, 24):
        for components in range(11):
            archive_num = 1
            while 1:
                try:
                    archive = '%dx-%d-%d'%(num_crossings,components,archive_num)
                    get_plaintext(archive)
                    archive_num += 1
                    print archive
                except:
                    break

def download_save(archive):
    '''
    Downloads the plaintext for the link with Knotilus archive number 'archive'
    (a string), and save it as 'archive.txt'. No other output.
    '''
    if not valid_archive_form(archive):
        raise KURLError('archive num must be of form ax-b-c, for a,b,c ints')

    filename = open(archive + '.txt', 'w') # create file to write link data to
    filename.write(get_plaintext(archive))
    filename.close()

def usage():
    print 'usage: python %s [-s] archive_num' % sys.argv[0]
    print 'optional [-s] to save link data to file archive_num.txt'
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        print get_plaintext(sys.argv[1])
    elif len(sys.argv) == 3:
        assert sys.argv[1] == '-s'
        download_save(sys.argv[2])
    else:
        usage()