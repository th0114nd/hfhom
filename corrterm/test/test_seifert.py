# Caltech SURF 2013
# FILE: test_seifert.py
# 08.22.13

'''
tests for seifert.py
'''

from seifert import *
import nose, random
from nose.tools import assert_raises


def test_invariants():
    assert invariants([1,(2,1),(3,4)]) == ([Fraction(1,2),Fraction(1,3)],\
                                           Fraction(17,6))
    assert invariants([-1, (2, -1), (2, -1), (3, -2)]) == \
           ([Fraction(1,2),Fraction(1,2),Fraction(1,3)],Fraction(-8,3))

def test_alter_data():
    pass # tested by assertion statements; also tested in test_weighted_graph.py

def test_cont_fraction():
    for test in range(100): # run 100 tests
        p = random.randint(1, 100)
        q = random.randint(1, 100)
        cont_frac = cont_fraction(p, q)
        cur_iter = cont_frac.pop()
        for i in range(len(cont_frac)):
            cur_iter = cont_frac.pop() - Fraction(1, cur_iter)
        if p > q:
            for i in cont_fraction(p, q):
                assert i >= 2
        assert cur_iter == Fraction(p, q)

def test_s_quad_form():
    quad_form1 = s_quad_form([0,(3,-1),(2,-1),(2,-1)], gui=False)
    assert numpy.array_equal(quad_form1[0],\
            numpy.array(\
                [[-3,1,0,1,1],
                 [1,-2,1,0,0],
                 [0,1,-2,0,0],
                 [1,0,0,-2,0],
                 [1,0,0,0,-2]]))
    assert quad_form1[1] == True
    
    quad_form2 = s_quad_form([-1,(2,1),(3,1),(5,1)], gui=False)
    assert numpy.array_equal(quad_form2[0], 
        numpy.array(\
            [[-2,1,1,0,1,0,0,0],
             [1,-2,0,0,0,0,0,0],
             [1,0,-2,1,0,0,0,0],
             [0,0,1,-2,0,0,0,0],
             [1,0,0,0,-2,1,0,0],
             [0,0,0,0,1,-2,1,0],
             [0,0,0,0,0,1,-2,1],
             [0,0,0,0,0,0,1,-2]]))
    assert quad_form2[1] == False
    
    # check negative definite (e+sum(pi/qi) != 0)
    assert_raises(ValueError, s_quad_form, [-2,(2,1),(3,2),(3,2),(6,1)], False)
    assert_raises(ValueError, s_quad_form, [2,(3,-2),(2,-1),(6,-5)], False)
        
    # trivial case
    assert numpy.array_equal(s_quad_form([-4], gui=False)[0], 
                             numpy.array([[-4]]))
    
    # test ignores q_i = 0
    assert numpy.array_equal(quad_form1[0], \
                             s_quad_form([0,(3,-1),(3,0),(2,-1),(2,-1)])[0])
    assert numpy.array_equal(quad_form2[0],\
                             s_quad_form([-1,(-1,0),(2,1),(3,1),(5,1)])[0])

if __name__ == '__main__':
    nose.runmodule()
