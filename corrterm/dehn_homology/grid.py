# Caltech SURF 2013
# FILE: grid.py
# 07.17.13

'''
do stuff with grid diagrams to prepare for CFK^\infty
'''

# winding matrix done by rows (consistent with gridlink)
# TODO bottom row first???

# TODO only knots no links...

from fractions import Fraction
import itertools # list(itertools.permutations([1,2,3]))
# TODO at this rate, we won't get past 7 crossings...
import math

def valid_xo(xlist, olist):
    '''
    Returns True if xlist, olist are valid (1 per row/col), False otherwise.
    '''
    if len(xlist) != len(olist):
        return False
    for col_num in range(len(xlist)):
        if xlist[col_num] == olist[col_num]:
            return False # same coordinates...
        if xlist.count(xlist[col_num]) != 1 or \
           olist.count(olist[col_num]) != 1:
            return False
    return True

def alexander_helper(x, o, winding, n):
    '''
    Returns -1/8 Sum(a(c_{i,j})) - (n-1)/2, where a(-) is minus the winding 
    number, and c_{i,j} is a corner of any square with an X or O.

    x       -- row indices of x's (starts at 0, at bottom)
    y       -- row indices of o's (starts at 0, at left)
    winding -- matrix of winding numbers TODO bottom to top ???
    n       -- size of grid
    '''
    a_rhs = 0
    for index, row in enumerate(x + o):
        # sum over winding numbers of corners
        a_rhs += winding[row][index%n] + winding[(row+1)%n][index%n] + \
            winding[row][(index+1)%n] + winding[(row+1)%n][(index+1)%n]
    a_rhs = Fraction(a_rhs, 8) - Fraction(n-1, 2)
    return a_rhs

def alexander(generator, winding, rhs):
    '''
    Returns Alexander grading of tuple 'generator'.
    
    generator -- tuple of row numbers
    winding   -- array of winding numbers TODO: bottom to top ???
    rhs       -- -1/8 Sum(a(c_{i,j})) - (n-1)/2, the right hand (constant) side
                 of the formula for Alexander grading
    '''
    asum = 0
    for index, row in enumerate(generator):
        asum += winding[row][index]
    asum *= -1
    asum += rhs
    assert asum.denominator == 1
    asum = asum.numerator
    return asum

def differby2(gen1, gen2):
    '''
    Returns tuple (True, [i1, i2]) if generators 'gen1' and 'gen2' differ
    by 2 points, where i1 and i2 are the indices (col) where they differ.
    Returns (False, []) otherwise.
    '''
    differ = 0
    where = []
    assert len(gen1) == len(gen2)
    for i in range(len(gen1)):
        if gen1[i] != gen2[i]:
            differ += 1
            where.append(i)
        if differ > 2:
            return (False, [])
    if differ != 2:
        return (False, [])
    return (True, where)

def interior(tup1, tup2, gen1, gen2, xlist, olist):
    '''
    Returns (True, [#X, #O]) if rectangle has no generators in it
    Returns (False, []) if rectangle has generators in it
    
    #X = number of X's in the rectangle
    #O = number of O's in the rectangle
    
    tup1 is the lower left corner of the rectangle
    tup2 is the upper right corner of the rectangle
    
    FIXME comment, test...might be off by 1
    '''
    n = len(gen1)
    
    assert gen1[tup1[0]] == tup1[1]
    assert gen1[tup2[0]] == tup2[1]
    
    # iterate - get appropriate columns, then check if rows are in rectangle
    if (tup1[0] < tup2[0] and tup1[1] >= tup2[1]) or \
       (tup1[0] > tup2[0] and tup1[1] <= tup2[1]) or (tup1[0] == tup2[0]):
        raise ValueError('points do not define a valid rectangle')
    if tup1[0] < tup2[0]: # normal
        col_indices = (tup1[0], tup2[0])
        row_indices = (tup1[1], tup2[1])
    else:
        col_indices = (tup2[0], tup1[0])
        row_indices = (tup2[1], tup1[1])
    
    # iterate through gen1, gen2 lists - make sure there are none
    for gen in (gen1[(col_indices[0]+1)%n:(col_indices[1]-1)%n] + \
                gen2[(col_indices[0]+1)%n:(col_indices[1]-1)%n]):
        if gen > row_indices[0] and gen < row_indices[1]: # inside rect
            return (False, [])
    
    num_x = 0
    num_o = 0
    
    # iterate through X list
    for x in xlist[col_indices[0]:col_indices[1]]:
        if x >= row_indices[0] and x < row_indices[1]: # inside rect
            num_x += 1
    
    # iterate through O list
    for o in olist[col_indices[0]:col_indices[1]]:
        if o >= row_indices[0] and o < row_indices[1]: # inside rect
            num_o += 1
    
    return (True, [num_x, num_o])

def differential(genlist, x, o, ak=False, k=0, b=False):
    '''
    Returns boundary operator del[genlist] = Sum over rect. y ([y, i-#X, y-#O])
    
    Output of [] means 0.
    
    'genlist' is a list of generators, where each generator is represented as
    a tuple ((r1, r2,...,rn), i, j). Multiple generators in the list 'genlist'
    indicates addition
    i.e. genlist = [((r1, r2,...,rn), i, j), ((s1, s2,...,sn), i', j')] means
    ((r1, r2,...,rn), i, j) + ((s1, s2,...,sn), i', j')
    
    x, o are lists of the positions of X's and O's, respectively.
    '''
    if ak and b: # both True
        raise ValueError('at least one of Ak^+, B+ must be False')
    # iterate over all other generators that differ by 2
    # i.e. start with x -> pick 2 points and swap them
    # C(n,2) = n(n-1)/2 = O(n^2)
    assert len(x) == len(o)
    boundary = {}
    for gen in genlist:
        rowtup = gen[0]
        assert len(rowtup) == len(x)
        for swap in [(i,j) for i in range(len(x)) for j in range(len(x)) \
                     if j > i]:
        # swap = column indices to swap; i < j always
            if rowtup[swap[0]] >= rowtup[swap[1]]:
                continue # not a valid rectangle i.e. y -> x not x -> y
            other_rowtup = list(rowtup)
            other_rowtup[swap[0]], other_rowtup[swap[1]] = \
                other_rowtup[swap[1]], other_rowtup[swap[0]] # swap positions
            other_rowtup = tuple(other_rowtup)
            result = interior((swap[0], rowtup[swap[0]]), \
                              (swap[1], rowtup[swap[1]]), rowtup, other_rowtup,\
                              x, o)
            if result[0] == True:
                # check Ak+, B+
                if ak and gen[1] - result[1][0] < 0 and gen[2] - result[1][1] < k: # i < 0, j < k
                    continue # skip (no arrow)
                if b and gen[1] - result[1][0] < 0: # i < 0
                    continue # skip (no arrow)
                other_gen = (other_rowtup, gen[1] - result[1][0], \
                             gen[2] - result[1][1])
                if other_gen in boundary:
                    del boundary[other_gen] # mod 2
                else:
                    boundary[other_gen] = 1
    return list(boundary) # all keys


if __name__ == '__main__':
    # trefoil sample - TODO: put this in test script
    winding=[[0,0,0,0,0],[0,0,1,1,1],[0,-1,0,1,1],[0,-1,-1,0,1],[0,-1,-1,-1,0]]
    x=[1,2,3,4,0]
    o=[4,0,1,2,3]
    rhs=alexander_helper(x,o,winding,5)
    count = {}
    generators = itertools.permutations([0,1,2,3,4])
    for i in range(math.factorial(5)):
        gen = generators.next() # FIXME: is next or list( ) faster?
        gr = alexander(gen,winding,rhs)
        if gr in count:
            count[gr] += 1
        else:
            count[gr] = 1
    print count
    print interior((0,3),(2,4),(3,0,4,1,2),(4,0,3,1,2),x,o) # Figure 3
    print interior((1,2),(4,3),(0,2,4,1,3),(0,3,4,1,2),x,o) # [1,1]
    print differential([((3,0,4,1,2),0,-3)],x,o)
    print differential(differential([((3,0,4,1,2),0,-3)],x,o),x,o)
    
# TODO section 2 cancel generators
# remove ONLY gen not reducing i, j in differential

# then compute homology on reduced generators

# size of grid = arc number
# alternating => crossings + 2, others less
# http://www.indiana.edu/~knotinfo/