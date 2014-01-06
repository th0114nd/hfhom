# Caltech SURF 2013
# FILE: homology.py
# 07.24.13

'''
homology CFK^\infty computations
'''

class HomNodeClass():
    def __init__(self, index):
        self.index = index
        self.startpt = [] # list of HomEdgeClass edges starting here
        self.endpt = [] # list of HomEdgeClass edges ending here

class HomEdgeClass():
    def __init__(self, index, start, end):
        self.index = index
        self.start = start # HomNodeClass
        self.end = end # HomNodeClass


def hom_generators(basis, edges):
    '''
    return set of generators for homology group
    
    basis is a list of sets (for the vertices)
    edges is a list of tuples of ints connecting sets
    
    simple example: basis = [set([1,2]),set([2,3,4]),set([1,4])] and 
                    edges = [(1,2),(1,3)]
    '''
    num_edges = len(edges)

def hom_generators_c(basis, edges):
    '''
    basis = list of HomNodeClass objects
    edges = list of HomEdgeClass objects
    does not modify basis or edges
    '''
    cur_edges = edges[:]
    cur_nodes = nodes[:]
    while 1:
        for end_edge in edge.end.endpt: # all edges with endpt X_j
            if end_edge == edge:
                continue
            end_edge.start = end_edge.start.symmetric_difference(end_edge.end)
            for start_edge in end_edge.start: # connect Y_k -> Y_l iff X_k->X_l xor X_i->X_l
                if edge.start in start_edge.end.startpt:
                    continue # don't connect since X_i->X_l
                # else, add edge Y_k->Y_l
        
        # delete stuff
        for edge2 in (edge.start.startpt).extend(edge.start.endpt):
            cur_edges[edge2.index] = None # delete all edges touching start
        for edge2 in (edge.end.startpt).extend(edge.end.endpt):
            cur_edges[edge2.index] = None # delete all edges touching end
        cur_nodes[edge.start] = None # delete X_i from list
        cur_nodes[edge.end] = None # delete X_j from list
        