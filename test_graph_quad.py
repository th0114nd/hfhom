# Caltech SURF 2013
# FILE: graph_quad_tests.py
# MENTOR: Professor Yi Ni
# 08.08.13

'''
Tests for graph_quad.py
'''

from graph_quad import *
import nose
from nose.tools import assert_raises

err = 0.00001 # error tolerance

#
# Graph tests 
#
def test_last_ancestor():
    num_nodes = 12
    gNodes = [NodeClass(i) for i in range(num_nodes)]
    gNodes[0].path = [0]
    gNodes[1].path = [0, 1]
    gNodes[2].path = [0, 1, 2]
    gNodes[3].path = [0, 3]
    gNodes[4].path = [0, 4]
    gNodes[5].path = [0, 3, 5]
    gNodes[6].path = [0, 3, 5, 6]
    gNodes[7].path = [0, 3, 5, 6, 7]
    gNodes[8].path = [0, 1, 8]
    gNodes[9].path = [0, 3, 5, 9]
    gNodes[10].path = [0, 3, 5, 6, 7, 10]
    gNodes[11].path = [0, 3, 5, 9, 11]    
    
    for i in range(num_nodes):
        assert gNodes[0].last_ancestor(gNodes[i]) == 0
        assert gNodes[i].last_ancestor(gNodes[0]) == 0
        if i in [1,2,8]:
            assert gNodes[1].last_ancestor(gNodes[i]) == 1
            assert gNodes[i].last_ancestor(gNodes[1]) == 1
        else:
            assert gNodes[1].last_ancestor(gNodes[i]) == 0
            assert gNodes[i].last_ancestor(gNodes[1]) == 0
            assert gNodes[2].last_ancestor(gNodes[i]) == 0
    assert gNodes[2].last_ancestor(gNodes[8]) == 1
    assert gNodes[11].last_ancestor(gNodes[10]) == 5
    assert gNodes[9].last_ancestor(gNodes[11]) == 9
    assert gNodes[7].last_ancestor(gNodes[9]) == 5
    assert gNodes[4].last_ancestor(gNodes[4]) == 4
    assert gNodes[6].last_ancestor(gNodes[3]) == 3
    assert gNodes[11].last_ancestor(gNodes[6]) == 5

# useful for test_edges_regions
def plink_load_objects(filename):
    data = load_plink(filename)
    gRegions = make_objects(data[0],data[1],data[2],data[3],data[4],data[5])[3]
    gNodes = [NodeClass(i) for i in range(len(gRegions))]    
    return edges_regions(gNodes, gRegions), gNodes    

# useful for test_edges_regions
def knotilus_load_objects(archive):
    gRegions = load(archive, False, False)[3]
    gNodes = [NodeClass(i) for i in range(len(gRegions))]
    return edges_regions(gNodes, gRegions), gNodes


edge_list_p1, nodes_p1 = plink_load_objects('testing/t1_p_multiloop.txt')
edge_list_p2, nodes_p2 = plink_load_objects('testing/t2_p_background.txt')
edge_list_p3, nodes_p3 = plink_load_objects('testing/t3_p_multiloop_background.txt')
edge_list_p4, nodes_p4 = plink_load_objects('testing/t4_p_normal.txt')
edge_list_k1, nodes_k1 = knotilus_load_objects('10x-2-1')
edge_list_k2, nodes_k2 = knotilus_load_objects('7x-1-2')

def test_edges_regions():
    # Test P1 - t1_p_multiloop.txt
    assert len(edge_list_p1) == 3
    assert edge_list_p1[0].edge == (0, 1)
    assert edge_list_p1[1].edge == (0, 1)
    assert edge_list_p1[2].edge == (1, 1)
    
    # Test P2 - t2_p_background.txt
    assert len(edge_list_p2) == 9
    edge_list_tuples = [y.edge for y in edge_list_p2]
    assert edge_list_tuples.count((0, 2)) == 4
    assert edge_list_tuples.count((0, 1)) == 1
    assert edge_list_tuples.count((0, 2)) == 4
    
    # Test P3 - t3_p_multiloop_background.txt
    assert len(edge_list_p3) == 7
    edge_list_tuples = [y.edge for y in edge_list_p3]
    assert edge_list_tuples.count((0, 1)) == 6
    assert edge_list_tuples.count((0, 0)) == 1
    
    # Test P4 - t4_p_normal.txt
    assert len(edge_list_p4) == 13
    edge_list_tuples = [y.edge for y in edge_list_p4]
    assert edge_list_tuples.count((0, 2)) == 4
    assert edge_list_tuples.count((0, 1)) == 1
    assert edge_list_tuples.count((1, 2)) == 4
    assert edge_list_tuples.count((2, 3)) == 4
    
    # Test Knotilus1 - 10x-2-1
    assert len(edge_list_k1) == 10
    edge_list_tuples = [y.edge for y in edge_list_k1]
    for edge in edge_list_tuples:
        assert edge_list_tuples.count(edge) == 1
    
    # Test Knotilus2 (background shaded) - 7x-1-2
    assert len(edge_list_k2) == 7
    edge_list_tuples = [y.edge for y in edge_list_k2]
    assert edge_list_tuples.count((0, 3)) == 4
    assert edge_list_tuples.count((0, 1)) == 1
    assert edge_list_tuples.count((2, 3)) == 1
    assert edge_list_tuples.count((1, 2)) == 1


def test_maximal_subtree():
    assert maximal_subtree([DirEdgeClass((0,0))], [NodeClass(0)]) == []
    # Test P1
    assert len(maximal_subtree(edge_list_p1, nodes_p1)) == 1
    
    # Test P2
    tree_p2 = maximal_subtree(edge_list_p2, nodes_p2)
    assert len(tree_p2) == 2
    assert tree_p2[0].edge == (0, 1)
    assert tree_p2[1].edge == (0, 2)
    
    # Test P3
    tree_p3 = maximal_subtree(edge_list_p3, nodes_p3)
    assert len(tree_p3) == 1
    assert tree_p3[0].edge == (0, 1)
    
    # Test P4
    tree_p4 = maximal_subtree(edge_list_p4, nodes_p4)
    assert len(tree_p4) == 3
    assert tree_p4[0].edge == (0, 1)
    assert tree_p4[1].edge == (0, 2)
    assert tree_p4[2].edge == (2, 3)
    
    # Test K1
    tree_k1 = maximal_subtree(edge_list_k1, nodes_k1)
    assert len(tree_k1) == 7
    assert [tree_k1[i].edge for i in range(7)] == [(0,1),(0,4),(0,5),(1,2),\
                                                   (3,4),(4,7),(5,6)]
    
    # Test K2
    tree_k2 = maximal_subtree(edge_list_k2, nodes_k2)
    assert len(tree_k2) == 3
    assert [tree_k2[i].edge for i in range(3)] == [(0,1), (0,3), (1,2)]

#
# Quadratic Form tests
#
def test_symmetric():
    array1 = numpy.array([[1,2,3],[0,4,5],[0,0,6]])
    symmetric(array1)
    assert numpy.array_equal(array1, numpy.array([[1,2,3],[2,4,5],[3,5,6]]))
    
    array2 = numpy.array([[1,2],[3,4]]) # not upper triangular
    assert_raises(AssertionError, symmetric, array2)

def test_circuit_and_shared_edges():
    #
    # test circuit
    #
    
    # Test P1
    c1 = circuit(maximal_subtree(edge_list_p1, nodes_p1), edge_list_p1[1], \
                 nodes_p1)
    assert len(c1[0]) == 1
    assert c1[0][0].edge == c1[1][0].edge == (0,1)
    # now check self loops are ok
    c12 = circuit(maximal_subtree(edge_list_p1, nodes_p1), edge_list_p1[2], \
                  nodes_p1)
    assert len(c12[0]) + len(c12[1]) == 1
    assert c12[0][0].edge == (1,1)
    
    # Test P3
    c3 = circuit(maximal_subtree(edge_list_p3, nodes_p3), edge_list_p3[1], \
                 nodes_p3)
    assert len(c3[0]) + len(c3[1]) == 2
    assert c3[0][0].edge == c3[1][0].edge == (0,1)
    # check self loops
    c32 = circuit(maximal_subtree(edge_list_p3, nodes_p3), edge_list_p3[6], \
                  nodes_p3)
    assert len(c32[0]) + len(c32[1]) == 1
    assert c32[0][0].edge == (0,0)
    
    # Test K1
    ck1 = circuit(maximal_subtree(edge_list_k1, nodes_k1), edge_list_k1[4], \
                  nodes_k1)
    # edge (2,3)
    assert len(ck1[0]) + len(ck1[1]) == 5
    assert ck1[0][1].edge == (1,2)
    assert ck1[1][1].edge == (0,4)
    ck12 = circuit(maximal_subtree(edge_list_k1, nodes_k1), edge_list_k1[-1], \
                   nodes_k1)
    # edge (5,7)
    assert len(ck12[0]) + len(ck12[1]) == 4
    assert ck12[0][1] == edge_list_k1[-1]
    assert ck12[1][0].edge == (4,7)
    
    #
    # test shared_edges
    #
    assert shared_edges(c1, c12) == 0
    assert shared_edges(c3, c32) == 0
    assert shared_edges(ck1, ck12) == -1

def test_shared_edges_more():
    edges = [DirEdgeClass((0,1)),DirEdgeClass((1,2)),DirEdgeClass((2,3)),\
            DirEdgeClass((3,4)),DirEdgeClass((0,4)),DirEdgeClass((0,4)),\
            DirEdgeClass((1,3)),DirEdgeClass((1,1))]
    c1 = ([edges[0], edges[1]], [edges[2], edges[3], edges[4]])
    c2 = ([edges[0]], [edges[6], edges[3], edges[4]])
    assert shared_edges(c1,c2) == -3
    c3 = ([edges[4]],[edges[5]])
    assert shared_edges(c3,c1) == 1
    c4 = ([edges[7]],[]) # self loop
    assert shared_edges(c4, c2) == shared_edges(c3, c4) == 0
    
def test_quad_form():
    # Test P1
    assert numpy.array_equal(quad_form(edge_list_p1, minus_maximal_subtree(\
        edge_list_p1, maximal_subtree(edge_list_p1, nodes_p1)), nodes_p1),\
        numpy.array([[-2,0],[0,-1]]))
    
    # Test P2
    # make the array for p2...
    p2_array = -1 * numpy.ones((7, 7), dtype=numpy.int)
    for i in range(3):
        p2_array[i,i] = -2
    for i in range(3, 7):
        for j in range(3, 7):
            if i != j:
                p2_array[i,j] = -2
            else:
                p2_array[i,i] = -3
    assert numpy.array_equal(quad_form(edge_list_p2, minus_maximal_subtree(\
        edge_list_p2, maximal_subtree(edge_list_p2, nodes_p2)), nodes_p2),\
        p2_array)
    
    # Test P3
    # make the array for p3...
    p3_array = -1 * numpy.ones((6, 6), dtype=numpy.int)
    p3_array[5] = [0 for i in range(6)]
    p3_array[:,5] = [0 for i in range(6)]
    for i in range(5):
        p3_array[i,i] = -2
    p3_array[5,5] = -1
    assert numpy.array_equal(quad_form(edge_list_p3, minus_maximal_subtree(\
        edge_list_p3, maximal_subtree(edge_list_p3, nodes_p3)), nodes_p3),\
        p3_array)
    
    # Test P4
    # make the array for p4...
    p4_array = numpy.zeros((10, 10), dtype=numpy.int)
    for i in range(3):
        for j in range(3, 7):
            p4_array[i,j] = -1
            p4_array[j,i] = -1
    for i in [0,1,2,7,8,9]:
        for j in [0,1,2,7,8,9]:
            if i != j and abs(i-j) < 3:
                p4_array[i,j] = -1
            else:
                p4_array[i,i] = -2
    for i in [3,4,5,6]:
        for j in [3,4,5,6]:
            if i != j:
                p4_array[i,j] = -2
            else:
                p4_array[i,i]=-3
    assert numpy.array_equal(quad_form(edge_list_p4, minus_maximal_subtree(\
        edge_list_p4, maximal_subtree(edge_list_p4, nodes_p4)), nodes_p4),\
        p4_array)
    
    # Test K1 10x-2-1
    assert numpy.array_equal(quad_form(edge_list_k1, minus_maximal_subtree(\
        edge_list_k1, maximal_subtree(edge_list_k1, nodes_k1)), nodes_k1),\
        numpy.array([[-5,-2,-1],[-2,-5,1],[-1,1,-4]]))
    
    # Test K2 7x-1-2
    assert numpy.array_equal(quad_form(edge_list_k2, minus_maximal_subtree(\
        edge_list_k2, maximal_subtree(edge_list_k2, nodes_k2)), nodes_k2),\
        numpy.array([[-2,-1,-1,-1],[-1,-2,-1,-1],[-1,-1,-2,-1],\
                     [-1,-1,-1,-4]]))
    
    # Test K3 23x-11-1
    edge_list_k3, nodes_k3 = knotilus_load_objects('23x-11-1')
    k3_array = numpy.zeros((12, 12), dtype=numpy.int)
    for i in range(9):
        k3_array[i][i] = -2
    k3_array[11, 11] = -2
    k3_array[9, 9] = k3_array[10, 10] = -12
    k3_array[9, 10] = k3_array[10, 9] = -11
    k3_array[9, 0:9] = k3_array[10, 0:9] = k3_array[0:9, 9] = \
        k3_array[0:9, 10] = [-1,-1,1,1,-1,1,-1,1,-1]
    k3_array[9,11] = k3_array[10,11] = k3_array[11,9] = k3_array[11,10] =\
        -1
    assert numpy.array_equal(quad_form(edge_list_k3, minus_maximal_subtree(\
            edge_list_k3, maximal_subtree(edge_list_k3, nodes_k3)), nodes_k3),\
            k3_array)
    
if __name__ == '__main__':
    nose.runmodule()