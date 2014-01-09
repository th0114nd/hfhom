# FILE: ndqf.py

import numpy as np
from smith import smith_normal_form
from fractions import Fraction, gcd
from sys import maxint
import time # timing
from multiprocessing import Pool, Manager
import functools

PROCESSES = None # number of processes in pool. 
# None => default is number of cpus counted

#from memory_profiler import profile

# TODO order for Z/5xZ/15 is a 5x15 array i.e. 0-14, 0-14, 0-14

def mod2(x, y): return (x - y) % 2

def process_alpha_outside(cls, representatives, alpha, lst):
    cls.process_alpha(representatives, lst, alpha)
    # for multiprocessing, can't pickle unless fcn is at top level of module

def nontrivial(mat):
    return np.matrix.copy(mat[mat!=1])

class NDQF(object):
    '''Represents a negative definite quadratic form.'''
    
    @classmethod
    def rational_inverse(cls, diag, left, right):
        '''
        Returns inverse of a rational matrix m with Smith normal form decomp
        diag, (left, right). i.e. left * diag * right = m.
        Then m^(-1) = right^(-1)diag^(-1)left^(-1).
        '''
        def flip(n):
            if n == 0:
                return 0
            else:
                return Fraction(1, n)
        new_left = np.rint(right.I).astype(int) # inverse of right
        new_right = np.rint(left.I).astype(int) # inverse of left
        # right, left unimodular => inverse is also an integer matrix
        return new_left * np.vectorize(flip)(diag) * new_right
    
    @classmethod
    def int_matrix(cls, mat, size):
        '''Returns int matrix that is the product of rational matrix 'mat'
        and common denominator, along with common denominator (int).
        Useful for speed (multiplying matrices with fractions is slow).'''
        def lcm(a, b): 
            '''least common multiple'''
            if a == 0 or b == 0:
                return 0
            return (a * b) / gcd(a, b)        
        entries = map(mat.item, xrange(size**2)) # all entries in matrix
        denoms = [entry.denominator for entry in entries]
        denom = abs(reduce(lcm, denoms))
        int_mat = np.asmatrix((denom * np.asarray(mat)).astype(int))
        return int_mat, denom
        
    def __init__(self, mat):
        '''Creates a quadratic form from an appropriate
        array-like value.'''
        try:
            m = np.matrix(mat)
        except Exception as e:
            raise ValueError("Must be convertible to a numpy matrix.")
        '''if not square(m):
            raise ValueError("Must be a square array to create a quad form.")
        if not negative_definite(m):
            raise ValueError("Must be a negative definite matrix.")
        if not symmetric(m):
            raise ValueError("Must be a symmetric array.")'''
        self.mat = m
        self.b = self.mat.shape[0]
        self.diagonal = (-np.diagonal(self.mat)).tolist()
        d, (u, v) = smith_normal_form(m)
        self.decomp = (d, (u, v))
        self.mat_inverse = NDQF.rational_inverse(d, u, v)
        self.int_inverse = NDQF.int_matrix(self.mat_inverse, self.b)
        self.compute_affine_space()
        self.compute_homology()
         
    def eval2(self, u, v, inverse=False):
        '''Evaluates the quadratic form on the vectors u and v. They should
        have appropriate lengths, but otherwise are autoconverted to the
        appropriate dimensions for Q(u, v) to be a scalar.'''
        u = np.matrix(u)
        v = np.matrix(v)
        if u.size == v.size == self.mat.shape[0]:
            u = u.reshape(1, u.size)
            v = v.reshape(v.size, 1)
            if inverse:
                return u * self.mat_inverse * v
            else:
                return u * self.mat * v
        else:
            raise ValueError("Inappropriately sized vectors for eval.")
    
    def eval(self, u):
        '''Returns value of |u|^2 = u(Q^-1)u as Fraction.'''
        u = np.matrix(u)
        return Fraction((u * self.int_inverse[0] * u.T)[0,0], self.int_inverse[1])
    
    def eval_int(self, u):
        '''Returns value of |u|^2 = u(Q^-1)u as Fraction.'''        
        u = np.matrix(u)
        return (u * self.int_inverse[0] * u.T)[0,0]
    
    def compute_homology(self):
        # The ith row of V corresponds to ZZ/D[i, i] in the module
        # ZZ^d / mat ZZ^d
        D, (U, V) = self.decomp
        self.group = Hom_Group(D, V)
       
    def compute_affine_space(self):
        '''Finds the basepoint of the affine space associated to the 
        quadratic form. The rest can be found by the action of the group.'''
        self.basepoint = np.diagonal(self.mat) % 2

    def find_abs(self, alpha):
        '''Find the absolute value |alpha|^2 for the matrix, that is
        max_v (alpha(v))^2 / Q(v, v). Returns as an int (numerator). 
        Denominator is self.int_inverse[1].'''
        return self.eval_int(alpha)

    def find_rep(self, coef_list):
        '''Finds a representative of the class for the coeficient list.
        Returns the vector 'basepoint + 2(c0 * gen[0] + c1 * gen[1]+ ...)'''
        unsummed = [2 * c * g for (c, g) in zip(coef_list, self.group.gen)]
        return self.basepoint + sum(unsummed)
    
    def process_alpha(self, representatives, alpha, lst):
        if map(mod2, self.diagonal, alpha) == [0 for i in xrange(self.b)]:
            class_index = self.equiv_class(alpha, representatives)
            magnitude = self.find_abs(alpha)
            if magnitude > lst[class_index]:
                lst[class_index] = magnitude
                # if get IndexError above, probably b/c did NOT find equiv class,
                # i.e. class_index went too high           
                
    def correction_terms_ugly(self):
        '''Finds the correction terms assoctiated to the quadratic form,
        for each of the equivalance classes it finds the maximum by
        iterating through the relation vectors of the group.'''
        print 'Not using multiprocessing'
        start_time = time.time()
        coef_lists = lrange(self.group.structure)
        # representatives = elements of C_1(V) (np.matrix)
        representatives = map(lambda l: self.find_rep(l), coef_lists)
        listofmaxes = [None for i in xrange(len(representatives))]
        alphagen = self.get_alpha()
        for alpha in alphagen:
            # check if a_i = Q(e_i,e_i) (mod 2)
            if map(mod2, self.diagonal, alpha) == [0 for i in xrange(self.b)]:
                class_index = self.equiv_class(alpha, representatives)
                int_magnitude = self.find_abs(alpha)
                if int_magnitude > listofmaxes[class_index]:
                    listofmaxes[class_index] = int_magnitude
                # if get IndexError above, probably b/c did NOT find equiv class,
                # so class_index too high
        # get corrterms via (|alpha|^2+b)/4
        print 'Computed from quadratic form in %g seconds' \
              % (time.time() - start_time)        
        return [Fraction(Fraction(alpha, self.int_inverse[1]) + self.b, 4) \
                for alpha in listofmaxes]
    
    #@profile
    def correction_terms_threaded(self):
        '''Finds the correction terms assoctiated to the quadratic form,
        for each of the equivalance classes it finds the maximum by 
        iterating through the relation vectors of the group. 
        
        Uses multiprocessing.'''
        print 'Using multiprocessing'
        pool = Pool() # default: processes=None => uses cpu_count()
        manager = Manager()
        start_time = time.time()
        coef_lists = lrange(self.group.structure)
        # representatives = elements of C_1(V) (np.matrix)
        representatives = map(lambda l: self.find_rep(l), coef_lists)
        # list of maxes        
        lst = manager.list([None for i in xrange(len(representatives))]) 
        alphalist = list(self.get_alpha()) # cannot pickle generators
        pool.map_async(functools.partial(process_alpha_outside, self, 
                                         representatives, lst), alphalist)
        pool.close()
        pool.join() # wait for pool to finish
        # get corrterms via (|alpha|^2+b)/4
        print 'Computed from quadratic form in %g seconds' \
              % (time.time() - start_time)
        return [Fraction(Fraction(alpha, self.int_inverse[1]) + self.b, 4) \
                        for alpha in lst]            
    def pretty_print(self, lst):
        '''Returns a string, created from lst with Fraction(a,b) written
        a/b'''
        # make Fractions pretty        
        pretty_list = ['%i/%i' %(f.numerator, f.denominator) \
                       if f.denominator != 1 else str(f.numerator) \
                       for f in lst]
        pretty_string = ', '.join(pretty_list)
        return pretty_string
    
    def correction_terms(self, multiprocessing=False):
        '''Finds the correction terms and returns them as strings instead of
        Fraction objects.'''
        print 'H_1(Y) ~ %s' % self.group.struct()
        if multiprocessing:
            corrterms = self.correction_terms_threaded()
        else:
            corrterms = self.correction_terms_ugly()
        corrterms = self.pretty_print(corrterms)
        print corrterms
        return corrterms
    
    #@profile
    def find(self, mat, rep):
        '''
        Returns True if 1-line np.matrix 'mat' is in the same equivalence class
        as np.matrix 'rep', False otherwise.
        
        Same equivalence class <=> differ by an element in 2q(V)
        Named for "Union-Find" programs
        '''
        # A = 2*self.mat; the rows of 2*self.mat generate 2q(V)
        # Same equivalence class iff mat + Ax = rep for an INTEGER matrix x
        # i.e. Ax = (rep - mat) => x = A^(-1)(rep - mat)
        # if x only has integers, then true; otherwise false
        # Avoids fractions (SLOW); so checks for integers using divisibility
        sol = self.int_inverse[0] * np.reshape(rep - mat, (-1,1))
        denom = 2 * self.int_inverse[1]
        for coord in sol: # check if actual sol (divide by denom) has all ints
            if coord[0,0] % denom:
                return False
        return True

    def equiv_class(self, mat, representatives):
        '''
        Returns the index of 'mat's equivalence class in list 'representatives'.
        '''
        index = 0
        for rep in representatives:
            if self.find(mat, rep):
                break
            index += 1
        return index
    
    def max_bounds(self):
        '''
        Return list of all possible values in 2q(V) (note must be even) s.t. 
        alpha := rep + val satisfies |a_i| <= -Q(e_i, e_i)
        '''
        # max_list - list [lst_1, lst_2, ... lst_b] where lst_i is a list of 
        #            possible values for a_i
        # max_list_sizes - list of the size of each list_i in max_list
        max_list = [range(-ndiag, ndiag+1) for ndiag in self.diagonal]
        max_list_sizes = [2*ndiag + 1 for ndiag in self.diagonal]
        return max_list, max_list_sizes
    
    def increment(self, counter, pos, diag):
        '''
        Increment list 'counter' in position 'pos' from the end.
        Modifies 'counter'. List 'diag' is the negative of the diagonal elements
        of Q; i.e. the 2nd output 'max_list_sizes' from max_bounds.
        
        Basically views counter as the coefficients in a weird base expansion.
        Also base expansion is 'read' left to right.
        When one digit reaches the max allowed value (base), it carries over
        to the digit to the right, and itself is set back to zero.
        '''
        if pos >= len(counter): # trying to increment when already at end
            raise ValueError('Cannot increment counter any further; at end')        
        if counter[pos] >= diag[pos]-1: # max allowed value at pos
            counter[pos] = 0 # reset to 0
            self.increment(counter, pos+1, diag)
        else: # not at max allowed value
            counter[pos] += 1
        return counter
    
    def get_alpha(self):
        '''
        Generates all possible values for alpha = [a_1,...,a_b] that satisfy
        |a_i|<=-Q(e_i,e_i)
        '''
        max_list, max_list_sizes = self.max_bounds()
        max_list_sizes2 = [val-1 for val in max_list_sizes]
        counter = [0 for i in xrange(self.b)] # which alpha coords to pick        
        for i in xrange(reduce(lambda x, y: x*y, max_list_sizes)):
            #alpha = [-self.diagonal[i] + counter[i] for i in xrange(self.b)]
            alpha = [max_list[i][counter[i]] for i in xrange(self.b)]
            yield alpha
            # update counter
            if counter != max_list_sizes2:
                self.increment(counter, 0, max_list_sizes)

class Hom_Group(object):
    '''A homology group.'''
    
    def __init__(self, diagonal, rows):
        '''Creates a new homology group using the list of invariant factors
        on the diagonal.'''
        invariant_factors = np.diagonal(diagonal)
        matters = nontrivial(invariant_factors) # all non-1 invariant factors
        # structure = [n1, n2, .. nk] if H1(Y) ~ ZZ/n1 x ZZ/n2 x ... ZZ/nk
        self.structure = matters.tolist()
        group_rank = len(self.structure)
        vect_dim = diagonal.shape[0]
        # The bottom row vectors in rows are the ones that generate the 
        # quotient module, subject to the top rows congruent to zero.
        start = vect_dim - group_rank
        self.gen = [rows[i] for i in range(start, vect_dim)] # generating vectors
        self.rel = [rows[i] for i in range(0, start)] # relation vectors ( = 0 )
        return
    
    def struct(self):
        '''Return structure of H_1(Y) as string'''
        def rep(i):
            '''The string representation of Z/i'''
            i = i if i > 0 else -i
            if i == 0:
                return "Z"
            elif i == 1:
                return "1"
            else:
                return "Z/" + str(i) + "Z"
        reps = map(rep, self.structure)
        if reps:
            structure = reduce(lambda s, z: s + 'x' + z, reps)
        else:
            structure = "1"
        return structure

    def __repr__(self):
        ''' Shows the structure of the group, as well as generators and
        relations.'''
        ret = []
        structure = self.struct()
        ret.append("Structure decomposition: H_1(Y) ~ " + structure + '.')
        ret.append("Generating vectors in order of invariant factor:")
        i = 0
        empty = True
        for row in self.gen:
            empty = False
            ret.append('    ' + str(row) + " has order " + 
                        str(self.structure[i]) + ".")
            i += 1
        if empty:
            ret.append("     (No generators, trivial)")
            empty = True
        ret.append("Relation vectors (congruent to 0):")
        for row in self.rel:
            empty = False
            ret.append('    ' + str(row))
        if empty:
            ret.append("     (No relations, free)")
        return '\n'.join(ret)

def lrange(index_list):
    '''Returns a generators that iterates over range(ind1) x range(ind2) ...'''
    if not index_list:
        yield []
    else:
        i = index_list[0]
        for i_sub in xrange(i):
            for l_sub in lrange(index_list[1:]):
                yield [i_sub] + l_sub

def nlrange(index_list):
    '''Returns a generator that is essentially range(-ind1+1, ind1) x ... 
    to traverse over a lattice.'''
    if not index_list:
        yield []
    else:
        i = index_list[0]
        for i_sub in xrange(-i + 1, i):
            for l_sub in nlrange(index_list[1:]):
                yield [i_sub] + l_sub

'''
a=NDQF([[-2, -1, -1],[-1, -2, -1],[-1, -1, -2]])
b=NDQF([[-2,  0,  0,  1,  1],
 [ 0,-2, -1, -1, -1],
 [ 0, -1, -2, -1, -1],
 [ 1, -1, -1, -3, -2],
 [ 1, -1, -1, -2, -3]])
c=NDQF([[-3, -1, -1,  0],[-1, -4, -2,  0],[-1, -2, -4,  1],[ 0,  0,  1, -3]])
ex=NDQF([[-5,2],[2,-4]])
ex2=NDQF([[-5,-2],[-2,-4]])
ex3=NDQF([[-2,1,0,0,0],[1,-3,1,1,0],[0,1,-2,0,0],[0,1,0,-2,1],[0,0,0,1,-2]])
os=NDQF([[-3,-2,-1,-1],[-2,-5,-2,-3],[-1,-2,-4,-3],[-1,-3,-3,-5]])
'''
'''
if __name__ == '__main__':
    os=NDQF([[-3,-2,-1,-1],[-2,-5,-2,-3],[-1,-2,-4,-3],[-1,-3,-3,-5]])
    os.correction_terms()
'''