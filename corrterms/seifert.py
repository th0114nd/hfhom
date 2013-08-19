# Caltech SURF 2013
# FILE: seifert.py
# AUTHOR: Laura Shou
# MENTOR: Professor Yi Ni
# 07.12.13

import numpy as np
import sys
import number_theory
from fractions import Fraction, gcd
from graph_quad import symmetric

DEBUG = False
class SeifertInputError(Exception):
    pass

def is_correct_form(listdata):
    '''
    Checks if the listdata is in the correct format. 
    The correct form is (e, [(p1,q1), (p2,q2), ... , (pr,qr)]), 
    where e and the pi's, qi's are integers, pi > 1, and gcd(pi,qi) = 1.
    '''
    e, pqlist = listdata
    if type(e) != int:
        return False

    for pair in pqlist:
        try:
            p, q = pair
            if q == 0 and DEBUG:
                print 'Warning: qi = 0, ignoring that pair'
            else:
                if p <= 1 or gcd(p, q) != 1:
                    return False
        except ValueError:
            return False
    return True

def negate(listdata):
    '''
    Returns the data for -Y, given the data 'listdata' for Y.
    
    Specifically, given 'listdata' (e, [(p1, q1), (p2, q2), ... , (pr, qr)]), 
    returns (-e, [(p1, -k1), (p2, -q2), ... , (pr, -qr)]).
    '''
    e, pairlist = listdata
    neglist = [(p, -q) for p, q in pairlist]
    return -e, neglist

def invariants(listdata):
    '''
    Returns the invariants ([qi/pi (mod 1)], e + sum(qi/pi)).
    
    Note [qi/pi (mod 1)] is a multiset; here it is returned as an ordered list
    since we will not be permuting the elements in the multiset in 'alter_data'.
    
    If qi = 0, the pair is ignored and not added to the multiset.
    '''
    multiset = []
    number, pairlist = listdata
    for p, q in pairlist:
        if q != 0:
            multiset.append(Fraction(q % p, p))
            number += Fraction(q, p)
    return multiset, number

def alter_data(listdata):
    '''
    Returns a tuple (list new_data, bool negate).
    
    new_data is data [e, (p1,q1), (p2,q2),...,(pr,qr)] for the Seifert fibered 
    rational homology sphere such that e > 0 and -pi < qi < 0.
    
    If the orientation is reversed, bool negate = True; if orientation need not
    be reversed to get e > 0 and -pi < qi < 0, negate = False.
    
    The oriented homeomorphism type of the Seifert fibered space is determined
    by the multiset {qi/pi (mod 1)} and number e + sum(qi/pi). As a result,
    we can alter the data by 
    (a) adding an integer to any qi/pi
    (b) subtracting that same integer from e, to make sure e + sum(qi/pi) stays
        the same
    In other words, we can replace (pi,qi) with (pi,qi+m*pi) and e with e-m,
    for some integer m. This function uses this method to get data with 
    e > 0 and -pi < qi < 0.
    '''
    minus = False
    e, pairlist = listdata
    new_pairlist = []
    for p, q in pairlist:
        if q == 0:
            continue
        elif p > q > 0:
                new_pairlist.append((p, q - p))
                e += 1
        elif q >= p > 0:
                   # 0 < p < q => get minimal m such that q - m*p < 0
                   # then certainly -p < q-m*p < 0 since else q-m*p <= -p,
                   # which would mean that q-(m-1)*p <= 0, contradicting the 
                   # minimality of m.
                new = q
                while 1:
                    new -= p
                    e += 1
                    if new < 0:
                        break
                new_data.append((p, new))
        elif q < p <= 0:
            new_data.append((p, q))
        elif p <= q < 0:
            if p <= -q: # add p to q until p > -q
                new = q
                while 1:
                    new += p
                    e -= 1
                    if p > -new:
                        break
                new_data.append((p, new))
    new_data[0] = e
    if e <= 0:
        minus = True
        # need to get -Y. After negating, e > 0, all pi > qi > 0. To get 
        # -pi < qi < 0, will just need to subtract pi from each qi => will be
        # adding r to e, so new e is still > 0.
        return alter_data(negate(new_data))[0], minus
    if DEBUG:
        assert invariants(listdata) == invariants(new_data)
        assert e > 0
        for pair in new_data[1:]:
            assert -pair[0] < pair[1] < 0
    return new_data, minus

def cont_fraction(p, q):
    '''
    Returns the (finite) continued fraction for p/q, where p, q are integers.
    p/q = a_0 -   1
                -----------
                a_1 - 1
                      ------
                      ..-1/a_n
    Returns [a_0, a_1,...,a_n]. Note the minus signs in the continued fraction
    expansion.
    '''
    # http://www.jcu.edu/math/vignettes/continued.htm
    cont_frac = []
    dividend = p
    divisor = q
    while 1: # Euclidean algorithm
        quotient = dividend/divisor
        remainder = dividend % divisor
        if remainder == 0:
            cont_frac.append(quotient)
            break
        cont_frac.append(quotient+1) # b/c of negative sign,
                                     # p = q*(quotient+1) - remainder'
        # don't actually care what remainder' is, but need original remainder to 
        # know when to break
        
        # prepare for next iteration
        dividend = divisor
        divisor = divisor - remainder
    return cont_frac

def s_quad_form(listdata):
    '''
    Returns the tuple (numpy.matrix quadratic_form, bool minus) of the weighted 
    'star-like' tree associated with the plumbed 3-manifold given by Seifert 
    data 'listdata'.
    
    minus = True if orientation of the manifold described by listdata has been
    reversed, False otherwise
    
    Input: listdata (e, [(p1, q1),...,(pr, qr)])
    
    The 'star-like' tree is formed as follows:
    Center node is a vertex with weight -e.
    There are r branches coming off of the center vertex.
    Each branch has the vertices [-a0, -a1, ... , -an], where a0,a1,...,an
    are the numbers in the continued fraction expansion of pi/qi, for each i.
    (Note: the continued fraction expansion has negative signs; see function
    'cont_fraction'.)
    
    The quadratic form of the weighted graph is defined by
    Q(v, v) = m(v), where m is the weight of the vertex
    Q(v, w) = 1 if v, w are connected by an edge, 0 otherwise
    '''
    if not correct_form(listdata):
        raise SeifertInputError, \
        '''data must be of the form 
        (e, [(p1, q1), (p2, q2), ... , (pr, qr)]) with gcd(pi,qi) = 1 and pi > 1'''
    (e, pairlist), minus = alter_data(listdata) # make e > 0, -pi < qi < 0
    tree = [e] # list of weights in star tree [e, a0, a1,...]
    branch_lengths = [] # list of lengths of branches in star tree, not 
                        # including start node
    for p, q in pairlist:
        branch = cont_fraction(p, -q)
        branch_lengths.append(len(branch))
        tree.extend(branch)
    size = sum(branch_lengths) + 1 # add start node
    row = 0
    column = 0
    # make the quadratic form matrix
    quad = np.matrix.zeros(shape=(size, size), dtype=np.int)
    # fill in the diagonal
    for index in range(size):
        quad[index,index] = -tree[index]
    # fill in the others (upper right triangle)
    cur_position = 1
    for length in branch_lengths:
        quad[0, cur_position] = 1 # star node
        for index in range(cur_position, cur_position+length-1):
            quad[index,index+1] = 1 # adjacent
        cur_position += length
    return symmetric(quad), minus
                
def usage():
    print 'usage: python %s e p1 q1 ... pr qr' % sys.argv[0]
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) == 1:
        usage()
    try:
        data = map(int, sys.argv[1:])
    except Error:
        usage() 
    e = data[0]
    pairs = [] 
    index = 1
    for index in range(1, len(data), 2):
        pairs.append(data[index], data[index+1])
    listdata = e, pairs
    print 'Inputted data:',
    print listdata
    print s_quad_form(listdata)
