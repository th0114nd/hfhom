# Caltech SURF 2013
# FILE: graph_quad.py
# 08.20.13

'''
Graph and quadratic form methods

Given the list of all RegionClass objects, this module has functions to create
the associated graph (RegionClass object => node, intersection => edge), 
maximal subtree, and quadratic form.

It also defines NodeClass and DirEdgeClass for the graph.

Nodes: NodeClass. The list Nodes is a list of NodeClass objects. However, other
                  lists of nodes in this module will generally be list of ints 
                  (the indices). Nodes will also generally be ints.
Edges: DirEdgeClass
Circuits: list of DirEdgeClass instances

As a script:
usage: python graph_quad.py [-s] archive_num
OR     python graph_quad.py -f archive_num.txt
OR     python graph_quad.py -p [filename]

[-s] to save Knotilus archive_num plaintext to archive_num.txt
-f to load archive_num.txt (Knotilus plaintext file)
-p to use Plink, [filename] to load file
'''

# useful for circuits: [y.edge for y in list_of_edges] is a list of the edges as
#                      tuples (node1_index, node2_index) instead of DirEdgeClass
#                      instances

import numpy, sys, tkFileDialog
from numpy import linalg as LA
from plink_classes import IntersectionClass
from plink_load import load_plink, make_objects
from knotilus_load import load


###############################
# Graph classes and functions #
###############################
class NodeClass():
    def __init__(self, index):
        self.index = index
        self.path = [] # list of nodes start_node -> self in max subtree
                       # uses ints, not NodeClass objects
                       # Note: len(self.path) = len(self.edge_path) + 1
        self.edge_path = [] # list of Edges start node -> self in max subtree
        self.edges = [] # list of all Edges with self as endpoint

    def last_ancestor(self, other):
        '''
        Return index of the last common ancestor of Nodes 'self' and 'other'. 
        Ancestor can be one of the given nodes if one node is an ancestor of the
        other.
        '''
        if self == other:
            return self.index
        path1 = self.path
        path2 = other.path
        ancestor = 0
        # make path1 the shorter one
        if len(path1) > len(path2):
            path1, path2 = path2, path1
        for index, node in enumerate(path1):
            # paths start out the same; last commmon ancestor is node right 
            # before paths differ
            if path2[index] != node:
                ancestor = path2[index-1] # the last node before they differed
                break
            ancestor = node # never differ=> one (node) is ancestor of the other
        return ancestor

class DirEdgeClass():
    def __init__(self, edge):
        self.edge = edge # 2-tuple (int, int) indices for NodeClass instances


def edges_regions(Nodes, Regions):
    '''
    Returns a list of all edges (DirEdgeClass) in the graph associated with 
    'Regions'.
    
    Each region becomes a node, and each intersection between regions becomes an
    edge in the graph (multiple edges and self loops allowed).
    
    Input:
    Nodes -- a list of all the NodeClass objects for the graph.
             These are "blank" NodeClass objects, i.e. their only non-empty 
             attribute is self.index. The other attributes will be added later.
             The should be len(Regins) of NodeClass objects.
    Regions -- a list of all the RegionsClass objects for the graph.
       
    This function also updates the NodeClass.edges attribute for all NodeClass
    objects in Nodes.
    
    Note: Evaluating [y.edge for y in output_list] gives the edges as ordered
    pairs. For example, [(0,2),(0,2),(0,1),(1,2)] means there are 2 edges 
    between the 0th and 2nd Regions, an edge between 0th and 1st Regions, and
    an edge between 1st and 2nd Regions.
    '''
    edge_list = []
    region_pairs = [(region1, region2) for region1 in Regions \
                    for region2 in Regions \
                    if Regions.index(region1) < Regions.index(region2)]
    for pair in region_pairs:
        for inter in range(pair[0].num_inter(pair[1])): 
            # for the number of intersections between the 2 regions in 'pair'
            index0 = Regions.index(pair[0])
            index1 = Regions.index(pair[1])
            new_edge = DirEdgeClass((index0, index1))
            edge_list.append(new_edge) # add edge b/w regions
            Nodes[index0].edges.append(new_edge) # update self.edges
            Nodes[index1].edges.append(new_edge) # ^(inter = edge index)
    # now check for self-loops, i.e. intersections that are visited twice.
    for region in Regions:
        for index, point in enumerate(region.vertices):
            if isinstance(point, IntersectionClass): 
            # vertices aren't visited twice
                if region.vertices.count(point) > 1 and \
                   index == region.vertices.index(point): 
                    # only want to count the 1st time inter is visited
                    region_num = Regions.index(region)
                    new_edge = DirEdgeClass((region_num, region_num))
                    edge_list.append(new_edge) # add self-loop!
                    Nodes[region_num].edges.append(new_edge) #update self.edges
    return edge_list
        
def maximal_subtree(edge_list, Nodes):
    '''
    Returns a list of edges (DirEdgeClass) of a maximal subtree of the graph 
    given by edge_list (DirEdgeClass objects).
    
    Maximal subtree algorithm (breadth first search):
    http://www.maths.qmul.ac.uk/~whitty/MTH6105/Weeks/Week2/Lectures/AGTW2L2.pdf
    
    Input:
    edge_list -- a list of all the edges (DirEdgeClass) of the tree. 
                 Output from 'edges_regions' is of this form.
    Nodes -- a list of all the NodeClass objects for the graph.
             They need to have self.edges filled in by 'edges_regions'.
       
    This function also updates the NodeClass.edge_path and NodeClass.path 
    attributes for all NodeClass objects in Nodes.
    '''    
    tree_edges = []  # all edges in the tree (DirEdgeClass objects)
    tree_nodes = [0] # all nodes in tree (ints)
    new_nodes = [0]  # new nodes to check
    Nodes[0].path = [0]     # set starting node's path
    Nodes[0].edge_path = [] # set starting node's edge_path
    done = False
    while done == False:
        done = True
        new_edges = []
        for node in new_nodes[:]:
            new_nodes.remove(node)
            
            # for each new node, check if any of the edges that aren't in the
            # tree connect to it AND don't connect to anything already in tree
            # (that would make a closed loop)
            for edge in Nodes[node].edges:
                # if we do have another edge leading away from the tree,
                # add it to our tree and keep going (done = False)
                if edge.edge[0] == node:
                    other_node = edge.edge[1]
                else:
                    other_node = edge.edge[0]
                if other_node not in tree_nodes: # add new node!
                    Nodes[other_node].edge_path = Nodes[node].edge_path +[edge]
                    Nodes[other_node].path = Nodes[node].path + [other_node]
                    new_nodes.append(other_node)
                    tree_nodes.append(other_node)                    
                    new_edges.append(edge)
                    done = False
        tree_edges.extend(new_edges)
    return tree_edges

def minus_maximal_subtree(list_of_edges, subtree):
    '''
    Return a list of all edges that were not included in the maximal subtree.
    '''
    all_edges_copy = list_of_edges[:]
    for edge in subtree:
        all_edges_copy.remove(edge)
    return all_edges_copy
        
        

############################
# Quadratic Form functions #
############################
def quad_form(tree, minus_edge_list, Nodes):
    '''
    Returns the quadratic form (numpy array) associated with the graph and 
    maximal subtree.
    
    Input:
    tree -- a list [edge1, edge2, etc.] of all the edges (DirEdgeClass) of the 
            maximal subtree
    minus_edge_list -- a list of all the edges (DirEdgeClass) in the graph that
                       are NOT in the maximal subtree
    Nodes -- a list of all the NodeClass objects in the graph. All attributes
             should be updated by 'edges_regions' and 'maximal_subtree'.
    '''
    size = len(minus_edge_list)
    row = 0
    column = 0
    # make the quadratic form matrix
    quad = numpy.zeros(shape=(size, size), dtype=numpy.int)
    # get edge pairs from minus_edge_list, but only the 'upper triangular' pairs
    # i.e. if have (edge1, edge2), don't get (edge2, edge1)
    edge_pairs = [(edge1, edge2) for index, edge1 in enumerate(minus_edge_list)\
             for edge2 in minus_edge_list[index:]]
    for edges in edge_pairs:
        quad[row, column] = shared_edges(circuit(tree, edges[0], Nodes), \
                                         circuit(tree, edges[1], Nodes))
        if column < size - 1:
            column += 1
        else: # end of array, go to next row
            row += 1
            column = row # start at main diagonal
    symmetric(quad) # fill in the 'bottom triangular' part
    assert is_negative_definite(quad)
    return quad

def symmetric(array):
    '''
    Takes an upper triangular square numpy array, and copies the upper 
    triangular part over to the lower left part to make a symmetric matrix.
    
    No output, but changes array. Raises ValueError if array is not upper
    triangular.
    '''
    size = array.shape[0]
    if size != array.shape[1]:
        raise ValueError('not a square matrix')
    for row in range(size):
        for column in range(size):
            if row > column: # lower triangle
                assert array[row][column] == 0
                array[row][column] = array[column][row]

def is_negative_definite(quad):
    '''
    Return True if square matrix/array 'quad' is negative definite
    (all eigenvalues negative), False otherwise.
    '''
    eigenvalues = LA.eigvalsh(quad)
    for eigen in eigenvalues:
        if eigen >= 0:
            print eigenvalues
            return False
    return True    

def circuit(tree, edge, Nodes):
    '''
    Return the circuit formed by 'edge' (DirEdgeClass) to the tree 'tree'.
    
    The circuit is represented as a 2-tuple. 
    The first element is a list of DirEdgeClass instances, 
    common_ancestor -> node1 -> node2.
    
    The second element is a list of DirEdgeClass instances,
    node2 -> common_ancestor. In this list, the coordinates of each edge
    (edge.edge) are the reverse of the direction actually traversed.
    '''
    node1 = edge.edge[0]
    node2 = edge.edge[1]
    ancestor = Nodes[node1].last_ancestor(Nodes[node2])
    index1 = Nodes[node1].path.index(ancestor)
    index2 = Nodes[node2].path.index(ancestor)
    
    edge_path1 = Nodes[node1].edge_path[index1:] # common_ancestor -> node1
    edge_path2 = Nodes[node2].edge_path[index2:] # common_ancestor -> node2
    edge_path2.reverse() # opposite order - want node2 -> common_ancestor
    return (edge_path1 + [edge], edge_path2)


def shared_edges(circuit1, circuit2):
    '''
    Returns the (signed) number of shared edges for 'circuit1' and 'circuit2'.
    
    Sign convention is negative if the circuits have the same orientation and 
    positive if they have opposite orientations.
    
    Note that no node or edge is visited more than once in each circuit, so
    we don't have to worry about duplicate edges.
    '''
    num_shared = 0
    orientation = 0
    
    for edge1 in circuit1[0]:
        if edge1 in circuit2[0]: 
            num_shared += 1
            assert orientation != 1 # orientation must be consistent
            orientation = -1 # going same direction (neither in reversed part)
        elif edge1 in circuit2[1]: # reversed edges
            num_shared += 1
            assert orientation != -1
            orientation = 1
    for edge1 in circuit1[1]: # reversed edges
        if edge1 in circuit2[1]:
            num_shared += 1
            assert orientation != 1
            orientation = -1
        elif edge1 in circuit2[0]: # reversed in circuit1, not rev. in circuit2
            num_shared += 1
            assert orientation != -1
            orientation = 1
    return orientation * num_shared

def graph_plot(edges):
    '''
    Return string command for Mathematica to plot graph.
    '''
    command_string = 'GraphPlot[{'
    for edge in edges:
        command_string += str(edge.edge[0]) + '->' + str(edge.edge[1]) + ','
    command_string = command_string[:-1] # remove last comma
    command_string += '}, VertexLabeling->True, MultiedgeStyle->.2]'
    return command_string

def usage():
    print 'usage: python %s [-s] archive_num' % sys.argv[0]
    print 'OR     python %s -f archive_num.txt' % sys.argv[0]
    print 'OR     python %s -p [filename]' % sys.argv[0]
    sys.exit(1)    

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == '-p': # Plink
            data = load_plink()
            all_data = make_objects(data[0],data[1],data[2],data[3],data[4],\
                                    data[5])            
            regions = all_data[3]
        else:
            regions = load(sys.argv[1], False, False)[3] # knotilus
    elif len(sys.argv) == 3:
        if sys.argv[1] == '-f':
            regions = load(sys.argv[2], True, False)[3]
        elif sys.argv[1] == '-s':
            regions = load(sys.argv[2], False, True)[3]
        elif sys.argv[1] == '-p': # Plink
            data = load_plink(sys.argv[2])
            all_data = make_objects(data[0],data[1],data[2],data[3],data[4],\
                                    data[5])           
            regions = all_data[3]
    else:
        usage()
    gNodes=[NodeClass(i) for i in range(len(regions))]
    t=edges_regions(gNodes,regions)
    m=maximal_subtree(t,gNodes)
    minus=minus_maximal_subtree(t, m)
    #print graph_plot(t) # entire graph
    #print graph_plot(m) # maximal subtree
    print quad_form(t,minus,gNodes)
    