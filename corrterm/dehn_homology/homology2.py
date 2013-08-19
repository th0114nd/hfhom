# Caltech SURF 2013
# FILE: homology2.py
# MENTOR: Professor Yi Ni
# 07.26.13

from copy import deepcopy
from grid import *

# problem: TODO FIXME how to handle Ak, B???

# FIXME shortcut- amanion file - cancel (ignore???) all differentials that 
# preserve i,j grading

graph = {0:[3],
         1:[3,4,5,6],
         2:[4,6,7],
         3:[],
         4:[],
         5:[],
         6:[],
         7:[]}

graph2 = {0:[1],
         1:[],
         2:[1]}

def make_graph(all_generators, x, o, simplify=False, ak=False, k=0, b=False):
    '''
    Returns tuple (graph_in_list_form, dict_of_generators).
    
    graph_in_list_form -- nodes = generators, directed arrows = boundary operator 
    dict_of_generators -- keys = generators of form ((x1,...xn),i,j), values = indices
    
    Input:
    all_generators -- list of generators of the form ((x1,...xn),0,j)
    x  -- 
    o  --
    simplify -- boolean value; True if want to ignore all differentials that preserve i and j grading
    ak -- boolean value; True if want to make graph for A_k^+
    k  -- int; value of k in A_k^+
    b  -- boolean value; True if want to make graph for B^+
    '''
    num_gen = len(all_generators)
    graph = {i:[] for i in range(num_gen)}
    graph_index = {key:index for (index, key) in enumerate(all_generators)}
    # graph_data fast way to look up index of a generator
    for generator in all_generators:
        igrading = generator[1]
        assert igrading == 0
        jgrading = generator[2]
        #boundaryleft = differential([generator], x, o, ak, k, b)
        boundary = differential([generator], x, o)
        for gen in boundary: # add new points
            if simplify and gen[1] == igrading and gen[2] == jgrading:
                continue # ignore differentials that preserve i, j gradings TODO is this ok???
            if not gen in graph_index:
                # add it (it's not on the j-axis; it's to the left)
                if (ak and (gen[1] >= 0 or gen[2] >= k)) or \
                   (b and gen[1] >= 0) or (not ak and not b):
                    graph_index[gen] = num_gen
                    graph[num_gen] = [] # no leaving arrows; will just ignore when calculating H*=ker/im
                    num_gen += 1                    
                
                # add copies to the right of the j-axis
                right_copy = (generator[0], igrading-gen[1], jgrading-gen[1]) # <- this is correct
                target = (gen[0], 0, gen[2]-gen[1])
                if right_copy in graph_index:
                    graph[graph_index[right_copy]].append(graph_index[target])
                else:
                    graph_index[right_copy] = num_gen
                    graph[num_gen] = [graph_index[generator]]
                    num_gen += 1
        if b:
            preserve_i = [gen for gen in boundary if gen[1] == 0] # only down, no left
            graph[graph_index[generator]].extend([graph_index[gen] for gen in boundary])
        elif ak:
            pass
        else:
            graph[graph_index[generator]].extend([graph_index[gen] for gen in boundary]) # make all the arrows to the left/down
    return graph, graph_index

def hom_generators(graph):
    '''
    determine generators for the homology of a complex C over F2=Z2.
    given graph 'graph' (list)
    "cancellation lemma" + Baldwin and Gillam
    '''
    cur_graph = deepcopy(graph) # want to be able to change lists (shallow copy doesn't work)
    # TODO don't deepcopy if modifying graph is ok (faster since no copying)
    cur_nodes = [set([i]) for i in range(len(cur_graph))]
    for xi in range(len(cur_nodes)): # loop through nodes
        if not xi in cur_graph:
            continue # deleted node already
        if cur_graph[xi] == []:
            continue # no edges starting at i
        xj = cur_graph[xi][0]
        for xk in cur_graph.keys(): # if xk=xj, no problem
            if xk == xi:
                continue
            if xj in cur_graph[xk]: # edge xk->xj; know xk!=xi
                # symmetric difference
                cur_nodes[xk] = cur_nodes[xk].symmetric_difference(cur_nodes[xi])
                # arrows:
                for xl in cur_graph.keys():
                    if xl == xi or xl == xj or xl == xk: # TODO faster xl in [xi,xj,xk]?
                        continue
                    xlin = xl in cur_graph[xk]
                    if (xl in cur_graph[xi]) != xlin: # xk->xl xor xi->xl 
                        if not xlin: # add xk->xl
                            cur_graph[xk].append(xl)
                cur_graph[xk].remove(xj) # deleting all edges ending at xj
            # else: no xk->xj => do nothing (leave edges as they are)
        
        # delete stuff
        del cur_graph[xi] # delete xi (and all edges starting at xi)
        cur_nodes[xi] = None
        del cur_graph[xj] # delete xj (and all edges starting at xj)
        cur_nodes[xj] = None
        for key in cur_graph.keys(): # delete all edges starting at xi
            if xi in cur_graph[key]:
                cur_graph[key].remove(xi)
    # get just the generators
    generators = []
    for node in cur_nodes:
        if node:
            generators.append(node)
    return generators

def hom_generators_cfk(graph, num_gen):
    '''
    num_gen -- # of generators on the j-axis
    determine generators for the homology of a complex C over F2=Z2.]
    CFK^\infty - removes everything NOT on j-axis at end TODO implement
    cancels those that preserve i,j grading TODO implement
    '''
    cur_graph = deepcopy(graph) # want to be able to change lists (shallow copy doesn't work)
    # TODO don't deepcopy if modifying graph is ok (faster since no copying)
    cur_nodes = [set([i]) for i in range(len(cur_graph))]
    for xi in range(len(cur_nodes)): # loop through nodes
        if not xi in cur_graph:
            continue # deleted node already
        if cur_graph[xi] == []:
            continue # no edges starting at i
        xj = cur_graph[xi][0]
        for xk in cur_graph.keys(): # if xk=xj, no problem
            if xk == xi:
                continue
            if xj in cur_graph[xk]: # edge xk->xj; know xk!=xi
                # symmetric difference
                cur_nodes[xk] = cur_nodes[xk].symmetric_difference(cur_nodes[xi])
                # arrows:
                for xl in cur_graph.keys():
                    if xl == xi or xl == xj or xl == xk: # TODO faster xl in [xi,xj,xk]?
                        continue
                    xlin = xl in cur_graph[xk]
                    if (xl in cur_graph[xi]) != xlin: # xk->xl xor xi->xl 
                        if not xlin: # add xk->xl
                            cur_graph[xk].append(xl)
                cur_graph[xk].remove(xj) # deleting all edges ending at xj
            # else: no xk->xj => do nothing (leave edges as they are)
        
        # delete stuff
        del cur_graph[xi] # delete xi (and all edges starting at xi)
        cur_nodes[xi] = None
        del cur_graph[xj] # delete xj (and all edges starting at xj)
        cur_nodes[xj] = None
        for key in cur_graph.keys(): # delete all edges starting at xi
            if xi in cur_graph[key]:
                cur_graph[key].remove(xi)
    # get just the generators
    generators = []
    for node in cur_nodes:
        '''if node:
            # discard all nodes that have no points on the j-axis
            jaxis = False # on j-axis or not
            for point in node:
                if point < num_gen: # in the original generators
                    jaxis = True
                    break
            if jaxis:
                generators.append(node)'''
        if node:
            generators.append(node)
    return generators

if __name__ == '__main__':
    # trefoil sample - TODO: put this in test script
    winding=[[0,0,0,0,0],[0,0,-1,-1,-1],[0,1,0,-1,-1],[0,1,1,0,-1],[0,1,1,1,0]]
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
    print differential([((3,0,4,1,2),0,-3)],x,o)
    print differential(differential([((3,0,4,1,2),0,-3)],x,o),x,o)    
    #print make_graph([((3,0,4,1,2),0,-3),((4,0,3,1,2),0,-3),((0,1,2,3,4),0,alexander((0,1,2,3,4),winding,rhs))],x,o)
    print '--------------------------------------------'
    generators = list(itertools.permutations([0,1,2,3,4]))
    for i in range(len(generators)):
        generators[i] = (generators[i], 0, alexander(generators[i],winding,rhs))
    graph3 = make_graph(generators,x,o,b=False)
    print hom_generators_cfk(graph3[0],120)
    print hom_generators_cfk(make_graph(generators,x,o,ak=False)[0],120)