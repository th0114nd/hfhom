import numpy as np
import functools
import itertools
import fractions as f
import numpy.linalg as la
import sys

verbose = False

def divides(a, b):
    ''' Checks if a | b'''
    if a == 0:
        return b == 0
    else:
        return b % a == 0

def gcd(a, b, xtra=True):
    '''Computes the gcd of a, and b: "The least positive integer g such
    that g | a, g | b, and if d | a, b then d | g, except for the case
    when a and b are 0. gcd(0, 0) = 0 is not positive". This routine
    also returns a pair of numbers u, v such that u * a + b * v = gcd(a, b).'''
    g, p = xgcd(np.absolute(a), np.absolute(b))
    if g < 0:
        p = [-p[0], -p[1]]
    if a < 0:
        p[0] = -p[0]
    if b < 0:
        p[1] = -p[1]

    if xtra:
        return np.absolute(g), p
    else:
        return np.absolute(g)

def xgcd(a, b):
    '''Used to find the gcd of positive numbers a, b and track the necessary
    solutions by flip flopping between a larger and smaller.
    Courtesy of rcampbel at umbc.edu/~rcampbel/Computers/Python/numbthy.html'''
    u1 = 1
    v1 = 0
    u2 = 0
    v2 = 1
    if b == 0:
        return a, [u1, v1]
    while True:
        quot = -(a // b)
        a = a % b
        u1 = u1 + quot * u2
        v1 = v1 + quot * v2
        if a == 0:
            return b, [u2, v2]
        quot = -(b // a)
        b = b % a
        u2 = u2 + quot * u1
        v2 = v2 + quot * v1
        if b == 0:
            return a, [u1, v1]
        
def nonzero_filter(mat):
    '''Returns a copy of mat with no zero elements, probably
    reshaped'''
    return np.copy(mat[mat!=0])

def is_diagonal(mat):
    '''Checks if the square matrix supplied is diagonal.'''
    diag = np.copy(mat) 
    for i in xrange(diag.shape[0]):
        diag[(i, i)] = 0
    return np.all(diag == 0)

def diagonal_chaining(mat):
    length = min(mat.shape[0], mat.shape[1])
    for i in xrange(length - 1):
        if not divides(mat[i, i], mat[i + 1, i + 1]):
            return False
    return True

def smith_normal_form_helper(mat, track_dict):
    '''Computes the Smith Normal form of the matrix mat, using a recursive
    algorithm provided by Havas and Majewski in their paper
    "Integer Matrix Diagonalization". The argument should be a numpy matrix
    of integers.'''
    # Keep reducing the pivot and changing it until we have an element and a 
    # block matrix:
    # a | 0 0 0
    # - \ - - -
    # 0 | * * *
    # 0 | * * *
    # 0 | * * *
    while not all_zero_facade(mat):
        pivot = mat[0, 0]
        # Track the remainder from dividing the facade (first row and column)
        # by the pivot, to reduce them down.
        least_rems_row = []
        for i in xrange(1, mat.shape[0]):
            q, r = div_alg(mat[i, 0], pivot)
            least_rems_row.append((i, q, r))
        least_rems_col = []
        for j in xrange(1, mat.shape[1]):
            q, r = div_alg(mat[0, j], pivot)
            least_rems_col.append((j, q, r))

        # Make the appropriate combinations to reduce the facade down.
        for i, q, r in least_rems_row:
            row_combine(mat, i, 0, -q, track_mat=track_dict['row_op'])
        for j, q, r in least_rems_col:
            col_combine(mat, j, 0, -q, track_mat=track_dict['col_op'])
        
        # Find and move the best candidate for the pivot
        i, j = best_pivot_facade(mat)
        row_swap(mat, i, 0, track_mat=track_dict['row_op'])
        col_swap(mat, j, 0, track_mat=track_dict['col_op'])
    return

def solve_diagonal(mat, track_dict):
    '''Reduces a diagonal matrix to another diagonal matrix with the
    appropriate divisibility property: each diagonal entry divides the next.'''
    if is_diagonal(mat) and diagonal_chaining(mat):
        # Just make sure that this element is positive
        if mat[0, 0] < 0:
            scale_row(mat, 0, -1, track_mat=track_dict['row_op'])
        return
    pivot = mat[0, 0]
    # Check that each member of the matrix is divisible
    # by the pivot. Note: this is somewhat wasteful, but
    # the zeros might not remain zeros after calling the helper.
    for i in xrange(mat.size):
        p = np.unravel_index(i, mat.shape)
        if not divides(pivot, mat[p]):
            col_ind = p[1]
            # Adding the column to the facade slates it for reduction.
            col_combine(mat, 0, col_ind, 1, track_mat=track_dict['col_op'])
            smith_normal_form_helper(mat, track_dict)
            x = divides(mat[0, 0], mat[p])
            pivot = mat[0, 0]
    solve_diagonal(mat[1:, 1:], track_dict)
    solve_diagonal(mat, track_dict)
    return

def _smith_normal_form(mat, track_dict):
    '''Destructively updates the matrix to change it to its smith_normal_form'''
    if np.all(mat == np.zeros(mat.shape)):
        return mat
    i, j = best_pivot_whole(mat)
    row_swap(mat, i, 0, track_mat=track_dict['row_op'])
    col_swap(mat, j, 0, track_mat=track_dict['col_op'])
    # Reduce mat to a block matrix form
    smith_normal_form_helper(mat, track_dict)
    # Diagonalize the sub block
    _smith_normal_form(mat[1:, 1:], track_dict)
    # Rearrange the diagonal to invariant factor form
    solve_diagonal(mat, track_dict)
    return mat

def smith_normal_form(mat):
    '''Creates a new matrix and sets it equal to the Smith Normal Form of mat:
    Finds a matrix D, such that U * D * v = mat for unimodular U and V, and 
    D is diagonal. The standard form is to have the diagonal entries correspond
    to the invariant factors: d[i] | d[i + 1].
    Use: Computes the invariant factor description from a presentation of a module,
    ZZ ^ (mat.length) / < mat.columns >'''
    x = np.matrix.copy(mat)
    # right_track watches the change of basis via the unimodular matrix to the right.
    # It's rows are the generators of the presented module.
    right_track = np.matrix(np.eye(x.shape[1])).astype(int)
    left_track = np.matrix(np.eye(x.shape[0])).astype(int)
    tracker = {'row_op':left_track, 'col_op':right_track}
    _smith_normal_form(x, tracker)
    return x, (tracker['row_op'], tracker['col_op'])

def all_zero_facade(mat):
    return np.all(mat[0,1:] == 0) and np.all(mat[1:, 0] == 0)

def div_alg(a, b):
    ''' Computes q, r such that a = q * b + r with |r| < b/2.'''
    if b == 0:
        return 0, a
    b_pos = np.absolute(b)
    a_pos = np.absolute(a)
    q = a // b
    r1 = a % b
    r2 = a % -b
    if (np.absolute(r1) <= np.absolute(r2)):
        return q, r1
    else:
        return q + 1, r2

def col_row_norm(mat, i, j):
    '''Computes the product of the euclidean norm of the row and column
    passing through mat[i, j]. Used as a basis for selecting pivot elements.'''
    col = np.copy(mat[i, :])
    row = np.copy(mat[:, j])
    return np.asscalar(np.dot(row.T, row) * np.dot(col, col.T))

def best_pivot_whole(mat, debug=False):
    '''Chooses the pivot in the matrix with least col_row_norm, and of those 
    chooses the one of least value.'''
    if debug:
        norm = lambda i, j : mat[i, j]
    else:
        norm = functools.partial(col_row_norm, mat)
    if np.all(mat == 0):
        return (0, 0)
    min_found = None
    mins = []
    mat_nonzero = nonzero_filter(mat)
    for p, val in np.ndenumerate(mat):
        mins, min_found = could_be_min(norm, mins, min_found, p, val)
    return select_smallest_index(mins)

def best_pivot_facade(mat, debug=False):
    if debug:
        norm = lambda i, j : mat[i, j]
    else:
        norm = functools.partial(col_row_norm, mat)
    if all_zero_facade(mat):
        return (0, 0)
    # Slices row 1 and column 1 off, then searches through
    # them sequentially for the index of minimal norm.
    row = mat[0, 1:]
    row_iter = np.ndenumerate(row)
    col = mat[1:, 0]
    col_iter = np.ndenumerate(col)
    mins = []
    min_found = None
    for p, val in row_iter:
        if val == 0:
            continue
        ind = 0, p[1] + 1
        mins, min_found = could_be_min(norm, mins, min_found, ind, val)
    for p, val in col_iter:
        if val == 0:
            continue
        ind = p[0] + 1, 0
        mins, min_found = could_be_min(norm, mins, min_found, ind, val)
    return select_smallest_index(mins)

def could_be_min(norm, mins, min_found, p, val):
    '''Compares norm(p) with the previously found minimum. Adds to 
    the list mins for later processing if equal, or clears the list if smaller.'''
    if val != 0:
        i, j = p
        poss = norm(i, j)
        if not min_found or poss < min_found:
            return  [(p, val)], poss
        elif poss == min_found:
            mins.append((p, val))
    return mins, min_found 

def select_smallest_index(mins):
    '''Runs through a list of ((i, j), val) tuples  and
    returns (i, j) of the val of least magnitude.'''
    ind = np.argmin(map(lambda p : np.absolute(p[1]), mins))
    return mins[ind][0]
    

def col_promote(ind, lit_mat, big_mat):
    '''Row and column operations here are performed on 
    block submatrices. They share a back corner with 
    the input matrix, so indices need to be translated for
    the tracking matrices. col_promote is used during a column
    operation, so ind corresponds to a column in the input matrix
    and row in the right tracking matrix.'''
    bigN = big_mat.shape[0]
    litN = lit_mat.shape[1]
    return bigN - litN + ind

def row_promote(ind, lit_mat, big_mat):
    '''See also col_promote. Except that this is a row in the
    input matrix and a column in the left tracking matrix.'''
    bigN = big_mat.shape[1]
    litN = lit_mat.shape[0]
    return bigN - litN + ind


# Credits to Jeremy Kun's blog[0] for these routines,
# as well as the ideas in his simultaneousReduce for watching the
# changes in the records as well as the center.
# [0]: jeremykun.com/2013/04/10

def row_swap(mat, i, l, track_mat=None):
    temp = np.copy(mat[i, :])
    mat[i, :] = mat[l, :]
    mat[l, :] = temp
    if verbose and i != l:
        print "After swapping rows {0} and {1}: ".format(i, l)
        print mat

    if track_mat is not None:
        # The tracker matrix and the submatrix share the back corner.
        bigI = row_promote(i, mat, track_mat)
        bigL = row_promote(l, mat, track_mat)
        col_swap(track_mat, bigI, bigL)

def col_swap(mat, j, k, track_mat=None):
    temp = np.copy(mat[:, j])
    mat[:, j] = mat[:, k]
    mat[:, k] = temp
    if verbose and j != k:
        print "After swapping cols {0} and {1}: ".format(j, k)
        print mat
    if track_mat is not None:
        bigJ = col_promote(j, mat, track_mat)
        bigK = col_promote(k, mat, track_mat)
        row_swap(track_mat, bigJ, bigK)

def scale_col(mat, i, c, track_mat=None):
    mat[:, i] *= c
    if verbose and c != 1:
        print "After scaling column {0} by a factor of {1}: ".format(i, c) 
        print mat 
    if track_mat is not None:
        bigI = col_promote(i, mat, track_mat)
        scale_row(track_mat, bigI, c)

def scale_row(mat, i, c, track_mat=None):
    mat[i, :] *= c
    if verbose and c != 1:
        print "After scaling row {0} by a factor of {1}: ".format(i, c)
        print mat
    if track_mat is not None:
        bigI = row_promote(i, mat, track_mat)
        print bigI
        print c
        scale_col(track_mat, bigI, c)

def col_combine(mat, addTo, scaling_col, scale_amt, track_mat=None):
    mat[:, addTo] += scale_amt * mat[:, scaling_col]
    if verbose and scale_amt != 0:
        msg  = "After adding {0} times colummn {1} to column {2}: "
        print msg.format(scale_amt, scaling_col, addTo)
        print mat

    if track_mat is not None:
        bigSR = col_promote(addTo, mat, track_mat)
        bigAT = col_promote(scaling_col, mat, track_mat)
        row_combine(track_mat, bigAT, bigSR, -scale_amt)

def row_combine(mat, addTo, scaling_row, scale_amt, track_mat=None):
    mat[addTo, :] += scale_amt * mat[scaling_row, :]
    if verbose and scale_amt != 0:
        msg ="After adding {0} times row {1} to row {2}: " 
        print msg.format(scale_amt, scaling_row, addTo)
        print mat
    if track_mat is not None:
        bigSC = row_promote(addTo, mat, track_mat)
        bigAT = row_promote(scaling_row, mat, track_mat)
        col_combine(track_mat, bigAT, bigSC, -scale_amt)

