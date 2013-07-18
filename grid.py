# Caltech SURF 2013
# FILE: grid.py
# 07.17.13

'''
do stuff with grid diagrams to prepare for CFK^\infty
'''

# winding matrix done by rows (consistent with gridlink)
# TODO bottom row first???

from fractions import Fraction
import itertools # list(itertools.permutations([1,2,3]))
# TODO at this rate, we won't get past 7 crossings...
import math

def alexander_helper(x, o, winding, n):
    '''
    row indices of x's (starts at 0, at bottom)
    row indices of o's
    matrix of winding numbers
    return -1/8 Sum(a(c_{i,j})) - (n-1)/2
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
    alexander grading
    tuple generator by row indices
    tuple generator, matrix of winding numbers
    rhs = -1/8 Sum(a(c_{i,j})) - (n-1)/2
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
    tup1 is lower left corner
    tup2 is upper right corner
    TODO could just use gen1, gen2 and run differby2 to get tup1, tup2...
    Returns (True, [#X, #O]) if rectangle has no generators in it 
    Returns (False, []) if rectangle has generators in it
    
    FIXME comment, test...might be off by 1
    '''
    n = len(gen1)
    
    # TODO: this part is unnecessary if remove tup1, tup2
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

def differential(genlist, x, o):
    '''
    list of tuples 'tuplist'
    [(x,i,j)] or [(x,i,j),(y,i',j')] for (x,i,j)+(y,i',j')
    
    TODO change if switch to generator classes??
    '''
    # iterate over all other generators that differ by 2...
    # i.e. start with x -> pick 2 points and swap them then compare...
    # C(n,2) = n(n-1)/2 = O(n^2)
    boundary = []
    for gen in genlist:
	for swap in [(i,j) for i in range(len(x)) for j in range(len(x)) if j > i]:
	    # swap = column indices to swap; i < j always
	    if gen[0][swap[0]] >= gen[0][swap[1]]:
		continue # not a valid rectangle i.e. y -> x not x -> y
	    other_gen = gen[:]
	    other_gen[0] = list(other_gen[0])
	    other_gen[0][swap[0]], other_gen[0][swap[1]] = other_gen[0][swap[1]], other_gen[0][swap[0]]
	    other_gen[0] = tuple(other_gen[0])
	    result = interior((swap[0], gen[0][swap[0]]), (swap[1], gen[0][swap[1]]), gen[0], other_gen[0], x, o)
	    if result[0] == True:
		boundary.append((other_gen[0], gen[1] - result[1][0], gen[2] - result[1][1]))
    return boundary

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
    print differential([[(3,0,4,1,2),0,-3]],x,o)