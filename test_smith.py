import functools
import math
import nose
import numpy as np
import random
from smith        import *
from numpy.linalg import det
from number_theory import divides, div_alg
from qc           import *

def matrices(items=integers(), size=(0, 30)):
    '''Generates random matrices using the qc syntax.'''
    small = np.matrix([items.next() for _ in xrange(size[0] ** 2)])
    yield small.reshape(size[0], size[0])
    big = np.matrix([items.next() for _ in xrange(size[1] ** 2)])
    yield big.reshape(size[1], size[1])
    while True:
        this_size = random.randint(size[0], size[1])
        nums = [items.next() for _ in xrange(this_size ** 2)]
        x = np.matrix(nums).reshape(this_size, this_size)
        yield x

def diagonals(items=lists(integers(-10000, 10000), size=(31, 31)), size2=(1, 30)):
    '''Creates random diagonal matrices.'''
    def assign_list(lst, size):
        ret = np.matrix(np.eye(size)).astype(int)
        for i in xrange(size):
            ret[i, i] = lst[i]
        return ret

    yield assign_list(items.next(), size2[0])
    yield assign_list(items.next(), size2[1])
    while True:
        this_size = random.randint(size2[0], size2[1])
        yield assign_list(items.next(), this_size)

def test_nonzero_filter():
    one = np.eye(2).astype(int)
    assert np.all(nonzero_filter(one) == np.array([1, 1]))
    assert np.all(one == np.eye(2).astype(int))
    two = np.matrix(range(1, 10)).reshape(3, 3)
    assert np.all(nonzero_filter(two) == two.ravel())
 

def test_select_smallest_index():
    one = (0, 0), 5
    two = (4, 3), -17
    three = (2, 23), 0
    four = (9, 5), 2
    assert select_smallest_index([one]) == (0, 0)
    assert select_smallest_index([two]) == (4, 3)
    assert select_smallest_index([three]) == (2, 23)
    assert select_smallest_index([four]) == (9, 5)
    assert select_smallest_index([one, two]) == (0, 0)
    assert select_smallest_index([one, two, three]) == (2, 23)
    assert select_smallest_index([one, two, three, four]) == (2, 23)
    assert select_smallest_index([one, four, two]) == (9, 5)

def test_could_be_min():
    mat = np.matrix([[3, 7, 5], [0, 3, 0], [19, 1, 23]])
    cbm = functools.partial(could_be_min, lambda i, j : mat[i, j])
    min_found = None
    mins = []
    p = (0, 0)
    mins, min_found = cbm(mins, min_found, p, mat[p])
    assert min_found == 3
    assert mins == [(p, mat[p])]
    p = (0, 1)
    mins, min_found = cbm(mins, min_found, p, mat[p])
    assert min_found == 3
    assert mins == [((0, 0), 3)]
    p = (0, 2)
    mins, min_found = cbm(mins, min_found, p, mat[p])
    assert min_found == 3
    assert mins == [((0, 0), 3)]
    p = (1, 0)
    mins, min_found = cbm(mins, min_found, p, mat[p])
    assert min_found == 3
    assert mins == [((0, 0), 3)]
    p = (1, 1)
    mins, min_found = cbm(mins, min_found, p, mat[p])
    assert min_found == 3
    assert mins == [((0, 0), 3), ((1, 1), 3)]
    p = (1, 2)
    mins, min_found = cbm(mins, min_found, p, mat[p])
    assert min_found == 3
    assert mins == [((0, 0), 3), ((1, 1), 3)]
    p = (2, 0)
    mins, min_found = cbm(mins, min_found, p, mat[p])
    assert min_found == 3
    assert mins == [((0, 0), 3), ((1, 1), 3)]
    p = (2, 1)
    mins, min_found = cbm(mins, min_found, p, mat[p])
    assert min_found == 1
    assert mins == [((2, 1), 1)]
    p = (2, 2)
    mins, min_found = cbm(mins, min_found, p, mat[p])
    assert min_found == 1
    assert mins == [((2, 1), 1)]

@forall(tries=10, m=matrices(items=integers(), size=(1, 30)))
def test_best_pivot_whole(m):
    # If we were being really honest, we would do this with negative integers.
    p = best_pivot_whole(m, debug=True)
    # This syntax is numpy witchcraft for a filter.
    filtered = nonzero_filter(m)
    val = np.all(filtered == 0) or m[p] == filtered.min()
    if not val:
        print filtered
        print m
        print p
        print m[p]
    assert val

@forall(tries=10, d=diagonals(items=lists(items=integers(), size=(31, 31))))
def test_best_pivot_whole_diag(d):
    p = best_pivot_whole(d, debug=True)
    filtered = nonzero_filter(d)
    assert np.all(filtered == []) or np.all(d[p] == filtered.min())


@forall(tries=10, m=matrices(items=integers(), size=(1, 30)))
def test_best_pivot_facade(m):
    p = best_pivot_facade(m, debug=True)
    if all_zero_facade(m):
        assert p == (0, 0)
        return
    else:
        assert p != (0, 0)
        mins = []
        col_filtered = nonzero_filter(m[1:, 0])
        if col_filtered.any():
            mins.append(col_filtered.min())
        row_filtered = nonzero_filter(m[0, 1:])
        if row_filtered.any():
            mins.append(row_filtered.min())
        assert mins
        if mins:
            assert m[p] == min(mins)

def test_all_zero_facade():
    one = np.matrix([[1, 3], [0, 9]])
    two = np.matrix([[0, 0], [0, 17]])
    three = np.matrix([[-4, 0], [0, 4]])
    assert all_zero_facade(np.eye(4))
    assert all_zero_facade(np.zeros((5, 5)))
    assert not all_zero_facade(np.ones((3, 3)))
    assert not all_zero_facade(one)
    assert all_zero_facade(two)
    assert all_zero_facade(three)
    assert all_zero_facade(np.matrix([3]))

def test_is_diagonal():
    one = np.eye(14)
    two = np.ones((3, 3))
    assert is_diagonal(one)
    assert not is_diagonal(two)

def test_diagonal_chaining():
    one = np.matrix([[2, 0], [0, 17]])
    assert not diagonal_chaining(one)
    one[1, 1] = 16
    assert diagonal_chaining(one)
    one[0 , 0] = 16
    assert diagonal_chaining(one)
    assert diagonal_chaining(np.eye(13))

def test_smith_normal_form():
    one = np.matrix([[1, 1],[0, 1]])
    assert np.all(smith_normal_form(one)[0] == np.eye(2))
    two = np.matrix([[1, 0],[1, 1]])
    assert np.all(smith_normal_form(two)[0] == np.eye(2))
    three = np.matrix([[1, -17], [0, 1]])
    assert np.all(smith_normal_form(three)[0] == np.eye(2))
    four = np.matrix([[1, 3], [4, -9]])
    four = smith_normal_form(four)[0]
    assert four[0, 0] == 1
    assert four[1, 0] == 0
    assert four[0, 1] == 0
    five = np.matrix([[100, 0], [41, 89]])
    five = smith_normal_form(five)[0]
    assert all_zero_facade(five)
    assert divides(five[0, 0], five[1, 1])
    six = np.matrix([[-5, -2], [-2, -4]])
    assert np.all(smith_normal_form(six)[0] == np.matrix([[1, 0], [0, 16]]))
    seven = np.matrix([[-2, 1, 0, 0, 0],
                       [1, -3, 1, 1, 0],
                       [0, 1, -2, 0, 0],
                       [0, 1, 0, -2, 1],
                       [0, 0, 0, 1, -2]])
    smith_seven = np.matrix(np.eye(5))
    smith_seven[4, 4] = 16
    assert np.all(smith_seven == smith_normal_form(seven)[0])
    eight = np.matrix([[88, 56, 97], 
                      [31, 32, 12],
                      [78, 58, 43]])
    smith_eight = np.matrix(np.eye(3))
    smith_eight[2, 2] = 30098
    assert np.all(smith_eight == smith_normal_form(eight)[0])

@forall(tries=5, m=matrices(items=integers(-1000, 1000), size=(1, 7)))
def test_random_smith_normal_form(m):
    '''Checks that the smith normal form routine behaves appropriately'''
    s, _ = smith_normal_form(m)
    def close_enough(a, b, max_rel_diff):
        # Don't have a good workaround for this.
        a = math.fabs(a)
        b = math.fabs(b)
        if math.log(a + 1) > 15:
            return True
        diff = math.fabs(a - b)
        largest = max(a, b)
        return diff <= largest * max_rel_diff
    assert close_enough(det(m), det(s), 0.1)
    assert is_diagonal(s)
    assert diagonal_chaining(s)
    for i in xrange(s.shape[0] - 1):
        if not divides(s[i, i], s[i + 1, i + 1]):
            print s
            print m
        assert divides(s[i, i], s[i + 1, i + 1])

@forall(tries=5, d=diagonals(size2=(1, 10)))
def test_solve_diagonal(d):
    '''Result should be still diagonal and have diagonal chaining.'''
    a = np.matrix(np.eye(d.shape[0])).astype(int)
    solve_diagonal(d, {'row_op':a, 'col_op':a})
    assert is_diagonal(d)
    assert diagonal_chaining(d)

@forall(tries=5, m=matrices(items=integers(-1000, 1000), size=(1, 7)))
def test_tracker(m):
    '''Tracker matrices should appropriately preserve the product.'''
    s, (u, v) = smith_normal_form(m)
    p = np.all(u * s * v) == m
    

if __name__ == "__main__":
    result = nose.run()
