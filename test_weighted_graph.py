# Caltech SURF 2013
# FILE: test_weighted_graph.py
# 08.22.13

'''tests for weighted_graph.py'''

from weighted_graph import *
import seifert
import nose, random
from nose.tools import assert_raises
from fractions import gcd

def test_missing_node():
    a = GraphPopup(None, gui=False)
    a.load('testing/forest_ex2.txt')
    assert a.missing_nodes() == set([])
    a.graph.remove_node('N15') # last node
    assert a.missing_nodes() == set([])
    a.graph.remove_node('N1')
    assert a.missing_nodes() == set([1])
    a.graph.remove_node('N0')
    assert a.missing_nodes() == set([0,1])
    
    b = GraphPopup(None, gui=False)
    b.load('testing/forest_ex1.txt')
    assert b.missing_nodes() == set([])
    b.graph.remove_node('N7')
    assert b.missing_nodes() == set([7])
    b.graph.remove_node('N8')
    b.graph.remove_node('N3')
    b.graph.remove_node('N10')
    assert b.missing_nodes() == set([3,7,8,10])

def test_is_forest():
    graph1 = nx.Graph()
    graph1.add_path([0,1,2,3])
    graph1.add_path([1,4,5])
    graph1.add_edge(0,6)
    assert is_forest(graph1) # tree
    graph1.add_edge(0,5)
    assert not is_forest(graph1)
    graph1.remove_edge(0,5)
    graph1.add_path([7, 8, 9])
    graph1.add_path([8, 10, 11])
    graph1.add_path([12, 13, 14])
    assert is_forest(graph1) # 3 disjoint trees

def test_g_quad():
    # check agrees with Seifert
    for i in range(200): # do this on 200 random Seifert datas
        listdata = []
        num_pairs = random.randint(0, 10)
        e = random.randint(-100, 100)
        listdata.append(e)
        for j in range(num_pairs):
            q = random.choice(range(-100,0) + range(1,101)) # exclude 0
            while 1: # change p until gcd(p, q) = 1
                p = random.randint(2, 100)
                if abs(gcd(p, q)) == 1:
                    break
            listdata.append((p,q))
        if seifert.invariants(listdata)[1] == 0:
            assert_raises(ValueError, seifert.s_quad_form, listdata, False)
            continue
        startree = seifert.make_graph(listdata)            
        assert numpy.array_equal(seifert.s_quad_form(listdata, gui=False)[0], 
                                 g_quad(startree,
            ['N%i'%index for index in range(len(startree.nodes(data=False)))]))
    # load some files
    graph1 = GraphPopup(None, gui=False)
    graph1.load('testing/forest_ex1.txt')
    nodes1 = ['N%i'%index for index in \
              range(len(graph1.graph.nodes(data=False)))]
    assert num_bad_vertices(graph1.graph, nodes1) == 1
    assert_raises(ValueError, g_quad, graph1.graph, nodes1, False) # not negdef
    graph1.load('testing/forest_ex2.txt')
    nodes2 = ['N%i'%index for index in \
              range(len(graph1.graph.nodes(data=False)))]
    assert num_bad_vertices(graph1.graph, nodes2) == 1
    assert numpy.array_equal(g_quad(graph1.graph, nodes2, gui=False), 
                             numpy.array(\
        [[-5,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0],
         [1,-3,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
         [1,0,-3,0,0,0,0,0,0,0,0,0,0,0,0,0],
         [1,0,0,-3,0,0,0,0,0,0,0,0,0,0,0,0],
         [0,0,0,0,-1,0,0,0,0,0,1,0,0,1,0,0],
         [1,0,0,0,0,-1,0,0,0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,-4,1,0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,1,-4,1,1,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,1,-1,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,1,0,-3,1,1,0,0,0,0],
         [0,0,0,0,1,0,0,0,0,1,-4,0,0,0,1,0],
         [0,0,0,0,0,0,0,0,0,1,0,-3,1,0,0,1],
         [0,0,0,0,0,0,0,0,0,0,0,1,-3,0,0,0],
         [0,0,0,0,1,0,0,0,0,0,0,0,0,-5,0,0],
         [0,0,0,0,0,0,0,0,0,0,1,0,0,0,-2,0],
         [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,-2]]))
    graph1.cancel()

if __name__ == '__main__':
    nose.runmodule()