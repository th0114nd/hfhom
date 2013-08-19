# Caltech SURF 2013
# FILE: weighted_graph.py
# 08.15.13

'''
negative-definite weighted graphs with at most 2 bad vertices

uses TreeClass and TreeNodeClass to get quadratic form
uses networkx to draw graphs
'''

from Tkinter import *
import networkx as nx
import matplotlib.pyplot as plt

import numpy
from numpy import linalg as LA
from graph_quad import symmetric

class TreeNodeClass(object):
    def __init__(self, weight, parent):
        self.weight = weight
        self.parent = parent
        self.children = [] # array of children nodes
        if parent:
            self.degree = 1 # parent, will count children later
        else:
            self.degree = 0 # root node
    
    def bad_vertex(self):
        return True if self.weight > -self.degree else False

class TreeClass(object):
    def __init__(self, nodes=[]):
        self.nodes = nodes # array of Nodes
    
    def add_node(self, weight, parent):
        new_node = TreeNodeClass(weight, parent)
        self.nodes.append(new_node)        
        if parent:
            parent.children.append(new_node)
            parent.degree += 1 # count children
    
    '''
    def delete_node(self, node_index):
        node = self.nodes[node_index]
        node.parent.children.remove(node) # update parent's children
        for child in node.children: # update children's parent
            child.parent = None
        self.nodes = self.nodes[:node_index] + self.nodes[node_index+1:] # remove
    '''
    
    def num_bad_vertices(self):
        num = 0
        for node in self.nodes:
            if node.bad_vertex():
                num += 1
        return num
    
    def g_quad_helper(self, node1, node2):
        if node1 == node2:
            return node1.weight
        all_edges = node2.children
        if node2.parent:
            all_edges.append(node2.parent)
        if node1 in all_edges:
            return 1 # connected by edge
        return 0
    
    def g_quad(self, gui=False):
        '''
        Return quadratic form (numpy array).
        '''
        if self.num_bad_vertices() >= 2:
            raise ValueError('More than two bad vertices')
        size = len(self.nodes)
        # make the quadratic form matrix
        quad = numpy.zeros(shape=(size, size), dtype=numpy.int)
        # fill in the matrix
        for (row, col) in [(row, col) for row in range(size) for col in range(size) if row <= col]:
            # fill in upper triangle part
            quad[row, col] = self.g_quad_helper(self.nodes[row], self.nodes[col])
        symmetric(quad)
        # check negative definite
        eigenvalues = LA.eigvalsh(quad)
        for eigen in eigenvalues:
            if eigen > 0:
                print quad
                raise ValueError('quadratric form is not negative definite')
        return quad     

class GraphPopup(object):
    def __init__(self, master, graph, tree):
        self.master = master
        self.master.title('Graph controls')
        
        self.nodes = []
        self.graph = graph
        self.num_nodes = 0
        
        self.tree = tree
        
        self.frame = Frame(master)
        self.frame.pack()
        
        # New node commands
        Label(self.frame, text='New node').grid(row=1, column=0)
        Label(self.frame, text='Parent').grid(row=0, column=1)
        self.n_parent_var = IntVar()
        self.n_parent_var.set(-1) # initial value
        self.n_parent_opt = [-1]
        self.n_parentmenu = OptionMenu(self.frame, self.n_parent_var, *self.n_parent_opt)
        self.n_parentmenu.grid(row=1, column=1)
        Label(self.frame, text='Weight').grid(row=0, column=2)
        self.n_weight = Entry(self.frame, width=4)
        self.n_weight.grid(row=1, column=2)
        Button(self.frame, text='Create', command=self.create_node).grid(row=1, column=3)
        
        separator = Frame(self.frame, height=2, bd=1, relief=SUNKEN)
        separator.grid(row=2, sticky='we', padx=5, pady=5, columnspan=5)        
        
        # Edit node commands
        Label(self.frame, text='Edit node').grid(row=4, column=0)
        Label(self.frame, text='Node #').grid(row=3, column=1)
        Label(self.frame, text='New parent').grid(row=3, column=2)
        Label(self.frame, text='New weight').grid(row=3, column=3)
        self.e_node_var = IntVar()
        self.e_parent_var = IntVar()
        self.e_node_var.set(0) # initial value
        #self.e_parent_var.set(-1) # initial value
        # Select which node to edit
        self.e_node_opt = [0,]
        self.e_nodemenu = OptionMenu(self.frame, self.e_node_var, *self.e_node_opt)
        self.e_nodemenu.grid(row=4, column=1)
        # Select a new parent
        self.e_parent_opt = ['same',-1,0]
        self.e_parentmenu = OptionMenu(self.frame, self.e_parent_var, *self.e_parent_opt)
        self.e_parentmenu.grid(row=4, column=2)
        self.e_weight = Entry(self.frame, width=4)
        self.e_weight.grid(row=4, column=3)
        
        Button(self.frame, text='Done', command=self.edit_node).grid(row=4, column=4)
        
        separator = Frame(self.frame, height=2, bd=1, relief=SUNKEN)
        separator.grid(row=5, sticky='we', padx=5, pady=5, columnspan=5)         
        
        '''
        # Delete node commands
        Label(self.frame, text='Delete node').grid(row=7, column=0)
        Label(self.frame, text='Node #').grid(row=6, column=1)
        # Select which node to delete
        self.d_node_var = IntVar()
        self.d_node_opt = [None,]
        self.d_nodemenu = OptionMenu(self.frame, self.d_node_var, *self.d_node_opt)
        self.d_nodemenu.grid(row=7, column=1) 
        Button(self.frame, text='Delete', command=self.delete_node).grid(row=7, column=3)

        separator = Frame(self.frame, height=2, bd=1, relief=SUNKEN)
        separator.grid(row=8, sticky='we', padx=5, pady=5, columnspan=5)
        '''
        Button(self.frame, text='Save', command=self.save).grid(row=9, column=1)
        Button(self.frame, text='Load new', command=self.load).grid(row=9, column=2)
        Button(self.frame, text='Close', command=self.close).grid(row=9, column=3)
        
        
        
        self.update_graph()
        
    def update_graph(self):
        plt.clf() # erase figure
        labels = dict((n, '%s,%s' %(n,a['weight'])) for n,a in self.graph.nodes(data=True))
        nx.draw(self.graph,labels=labels,node_size=1000)
        plt.show()
    
    def save(self):
        pass
    
    def load(self):
        pass
    
    def create_node(self):
        try:
            n_weight = int(self.n_weight.get())
        except:
            raise ValueError('no data for weight or not an int')
        new_name = 'N%i' % self.num_nodes
        parent_index = self.n_parent_var.get()
        self.graph.add_node(new_name, parent=parent_index, weight=n_weight)
        self.nodes.append(new_name)
        if self.num_nodes != 0:
            # manage parent node info
            parent_node = self.nodes[parent_index]
            self.graph.add_edge(parent_node, new_name)
        #else:
            # remove -1 option
            #self.n_parent_opt = []
            #self.n_parent_var.set(0)
        # update dropdown menu
        self.n_parent_opt.append(self.num_nodes)
        self.n_parentmenu.destroy()
        self.n_parentmenu = OptionMenu(self.frame, self.n_parent_var, *self.n_parent_opt)
        self.n_parentmenu.grid(row=1, column=1)
        
        if self.num_nodes != 0:
            # update Edit dropdown menu
            self.e_node_opt.append(self.num_nodes)
            #self.e_nodemenu.destroy()
            self.e_nodemenu = OptionMenu(self.frame, self.e_node_var, *self.e_node_opt)
            self.e_nodemenu.grid(row=4, column=1)
            
            self.e_parent_opt.append(self.num_nodes)
            #self.e_parentmenu.destroy()
            self.e_parentmenu = OptionMenu(self.frame, self.e_parent_var, *self.e_parent_opt)
            self.e_parentmenu.grid(row=4, column=2)
        
        if self.num_nodes != 0:
            self.tree.add_node(n_weight, t.nodes[parent_index])
        else:
            self.tree.add_node(n_weight, None)        
        
        self.num_nodes += 1
        self.update_graph()
    
    def edit_node(self):
        if self.num_nodes == 0:
            raise ValueError('no nodes to edit')
        node = self.e_node_var.get()
        old_parent = self.graph.node[self.nodes[node]]['parent']
        try:
            e_parent = self.e_parent_var.get()
            self.graph.remove_edge(self.nodes[node], self.nodes[old_parent])
            self.graph.add_edge(self.nodes[node], self.nodes[e_parent])
            self.graph.node[self.nodes[node]]['parent'] = e_parent
            print 'Removing edge from %s to %s' %(self.nodes[node], self.nodes[old_parent])
            print 'Adding edge from %s to %s' %(self.nodes[node], self.nodes[e_parent])
            # update TreeClass parent and children
            self.tree.nodes[node].parent = self.tree.nodes[e_parent]
            self.tree.nodes[e_parent].children.append(self.tree.nodes[node])
            self.tree.nodes[old_parent].children.remove(self.tree.nodes[node])
        except ValueError:
            pass # chose string 'same' => ignore
        try:
            weight = self.e_weight.get()
            if weight != '':
                self.graph.node['N%i'%node]['weight'] = weight # update graph to draw
                self.tree.nodes[node].weight = weight # update TreeClass
        except ValueError:
            raise ValueError('Invalid weight')
        
        self.update_graph()
        
    '''
    def delete_node(self):
        node = self.d_node_var.get()
        # remove networkx node:
        self.graph.remove_node(self.nodes[node])
        self.nodes = self.nodes[:node] + self.nodes[node+1:]
        # remove TreeClass node
        self.tree.remove(self.tree.nodes[node])
    '''
    
    def close(self):
        print t.g_quad()
        plt.close()
        self.frame.destroy()
        #self.master.quit()
        

if __name__ == '__main__':
    a = TreeClass()
    
    G = nx.Graph()
    t = TreeClass()
    
    root = Tk()
    root.geometry('350x200')
    
    app = GraphPopup(root, G, t)
    
    root.mainloop()