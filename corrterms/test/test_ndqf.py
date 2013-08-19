#!/usr/bin/python
import nose
from ndqf import *

def test_lrange():
    zero = lrange([0])
    one = lrange([1])
    two = lrange([1, 1])
    three = lrange([2, 1])
    four = lrange([1, 5])
    five = lrange([3, 4])
    six = lrange([90, -3, 4])
    seven = lrange([2, 0, 2])
    def gen_to_list(gen):
        return [x for x in gen]
    assert gen_to_list(zero) == []
    assert gen_to_list(one) == [[0]]
    assert gen_to_list(two) == [[0, 0]]
    assert gen_to_list(three) == [[0, 0], [1, 0]]
    assert gen_to_list(four) == [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]]
    assert gen_to_list(five) == [[0, 0], [0, 1], [0, 2], [0, 3],
                           [1, 0], [1, 1], [1, 2], [1, 3],
                           [2, 0], [2, 1], [2, 2], [2, 3]] 
    assert gen_to_list(six) == []
    assert gen_to_list(seven) == []

def test_nlrange():
    zero = nlrange([0])
    one = nlrange([1])
    two = nlrange([1, 1])
    three = nlrange([2, 1])
    four = nlrange([2, 2])
    five = nlrange([1, 5])
    six = nlrange([3, 4])
    seven = nlrange([90, -3, 4])
    eight = nlrange([2, 0, 2])
    def gen_to_list(gen):
        return [x for x in gen]
    assert gen_to_list(zero) == []
    assert gen_to_list(one) == [[0]] 
    assert gen_to_list(two) == [[0, 0]]
    assert gen_to_list(three) == [[-1, 0], [0, 0], [1, 0]]
    assert gen_to_list(four) == [[-1, -1], [-1, 0], [-1, 1],
                                [0, -1], [0, 0], [0, 1],
                                [1, -1], [1, 0], [1, 1]]
    assert gen_to_list(five) == [[0, x] for x in range(-4, 5)]
    assert gen_to_list(six) == [[x, y] for x in range(-2, 3) for y in range(-3, 4)]
    assert gen_to_list(seven) == []
    assert gen_to_list(eight) == []

def test_hom_group():
    one = np.matrix([[1, 0], [0, 1]])
    g_one = Hom_Group(one, one)

def test_linear_combos():
    vone = []
    vtwo = [[1]]
    vthree = [[1, 2], [4, 5]]
    vfour = [[-3, -4, 17, 3.4], [-3,8, 4, 2], [1, 0, -1, 0]]
    cone = []
    ctwo = [2]
    cthree =[3, 4, 5]
    cfour = [[1, 0], [0, 1]]
    cfive = [[1, 1], [-1, 1], [2, 3]]
    csix = [[1, 1, 0], [0, 0, 1]]
    def toList(vs, cs): return [x for x in linear_combos(vs, cs)]
    one = toList(vone, cone)
    assert(one == [])
    two =  toList(vtwo, cone)
    assert(two == [])
    three = toList(vtwo, ctwo)
    assert(three == [[2]])
    four = toList(vtwo, cthree)
    assert(four == [[3], [4], [5]])
    five = toList(vthree, cfour)
    assert(np.all(five == [[1, 2], [4, 5]]))
    six = toList(vthree, cfive)
    assert(np.all(six == [[5, 7], [3, 3], [14, 19]]))
    seven = toList(vfour, csix)
    assert(np.all(seven == [[-6, 4, 21, 5.4], [1, 0, -1, 0]])) 

if __name__=="__main__":
    result = nose.run()
