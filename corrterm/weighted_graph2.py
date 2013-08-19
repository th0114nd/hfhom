# Caltech SURF 2013
# FILE: weighted_graph2.py
# 08.16.13

'''
negative-definite weighted graphs with at most 2 bad vertices

uses networkx to draw graphs and get quadratic form
'''

# Notes: had to put class OutputWindow in a separate file so could be imported...
# cannot call OutputWindow from gui.py since wait_window() will wait until
# everything is closed
# seems to only be a problem when pyplot is called; works fine when pyplot never activates...
# (can't figure out how to close everything otherwise)

# TODO it is recommended you do NOT edit the exported files by hand
# missing a numbered node will fail

# TODO Edit node -> make sure can't pick self as parent

# TODO check if Tree

# TODO handle empty graph case

# TODO when loading, add nodes to stuff - must FIX dropdown AND FIX numbering
# (start numbering at correct node #, not 0)

# Known issues
# clumsy interface
# cannot handle missing nodes
# cannot delete nodes

from Tkinter import *
import tkFileDialog, tkMessageBox
import networkx as nx
import matplotlib.pyplot as plt
import traceback

from gui_output import OutputWindow

import numpy
from numpy import linalg as LA
from graph_quad import symmetric    

class GraphPopup(Frame):
    def __init__(self, master, graph, condense, show_quad):
        self.master = master
        self.top = Toplevel(master)
        self.top.title('Graph controls')
        
        self.condense = condense # variable
        self.show_quad = show_quad # variable
        
        self.info = 'unknown' # inputinfo for the output window
        
        self.nodes = []
        self.graph = graph
        self.num_nodes = 0
        
        self.frame = self.top
        #self.frame = Frame(self.top)
        #self.frame.pack()
        
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
        Button(self.frame, text='Load', command=self.load).grid(row=9, column=2)
        Button(self.frame, text='Done/Close', command=self.close).grid(row=9, column=3)
        
        
        
        #self.update_graph() # show matplotlib drawing screen
        
    def update_graph(self):
        plt.clf() # erase figure
        labels = dict((n, '%s,%s' %(n,a['weight'])) for n,a in self.graph.nodes(data=True))
        nx.draw(self.graph,labels=labels,node_size=1000)
        plt.show()
    
    def save(self):
        '''save as adjacency list'''
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        filename = tkFileDialog.asksaveasfilename(**options)
        
        if filename:
            adjfile = open(filename, 'wb')
            nx.write_adjlist(self.graph, adjfile)            
            adjfile.write('\nDATA\n')
            adjfile.write(str(self.graph.nodes(data=True)))
            adjfile.close()
            print 'Graph data saved to %s' % filename
            self.info = filename
    
    def load(self, gui=False):
        '''load adjacency list from file'''
        # open file options
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        filename = tkFileDialog.askopenfilename(**options)

        if filename == '': # canceled
            return
        # attempt to open file
        try:
            adjfile = open(filename, 'r')
            self.info = filename
        except:
            if not gui:
                print 'Cannot open file %s' % filename
                print 'Aborting operation; please try again'
                raise IOError('failed to open file')
            else: # gui -> messagebox
                tkMessageBox.showwarning('Open file','Cannot open file %s.' %filename \
                                         +'Aborting operation; please try again.')
                raise IOError('failed to open file')
        # get the adjacency list
        adjlist = [] # list of strings
        try:
            while 1:
                line = adjfile.readline()
                if not line: # 'DATA' line should come before EOF
                    raise IOError('failed to load - possibly no graph data')
                if line[:4] == 'DATA':
                    break
                if line[0] == '#' or line == '' or line == '\n': # skip
                    continue
                adjlist.append(line[:-1]) # don't want \n char
            self.graph = nx.parse_adjlist(adjlist) # got graph
            if not self.is_tree():
                raise ValueError('not a tree')
            # get the node data - must be preceded by a line starting with 'DATA'
            while 1:
                node_data = adjfile.readline()
                if not node_data:
                    raise IOError('no data')
                if node_data != '' and node_data != '\n':
                    break
            # add node attributes (weight, parent)
            # convert node_data (string) to list FIXME EVAL
            for node in eval(node_data):
                for attr in node[1].keys():
                    self.graph.node[node[0]][attr] = node[1][attr] # node[1] is a dict of attr
            # update self.nodes (keep in order)
            num_nodes = len(self.graph.nodes(data=False))
            for index in range(num_nodes):
                self.nodes.append('N%i' % index)
        except Exception as error:
            tkMessageBox.showwarning('Loading', \
                                     'Loading failed - %s%s'%(type(error),\
                                                              filename))
            print traceback.print_exc()
            return
        
        # update graph control options
        self.n_parent_opt = range(-1, num_nodes)
        self.e_node_opt = range(num_nodes)
        self.e_parent_opt = ['same']
        self.e_parent_opt.append(range(-1, num_nodes))
        
        print 'Graph data successfully loaded from %s' % filename        
        self.update_graph()
    
    def is_tree(self):
        '''Return True if self.graph is a tree, False otherwise.'''
        return True # TODO FIXME DO THIS SOON
    
    def missing_node(self, num_nodes):
        '''
        Return True if self.graph is missing a node, False otherwise.
        
        By 'missing a node', mean that node numbering skips from, eg. N1 to N3,
        with N2 missing.
        '''
        nodes = self.graph.nodes(data=False)
        indices = []
        for node in nodes:
            indices.append(int(node[1]))
        if set(indices) == set(range(num_nodes)):
            return False
        return True
    
    def create_node(self):
        '''Create a new node from the "Create New" options.'''
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
        
        self.num_nodes += 1
        self.update_graph()
    
    def edit_node(self):
        '''Edit node according to "Edit node" options.'''
        if self.num_nodes == 0:
            raise ValueError('no nodes to edit')
        node = self.e_node_var.get()
        old_parent = self.graph.node[self.nodes[node]]['parent']
        try:
            e_parent = self.e_parent_var.get()
            self.graph.remove_edge(self.nodes[node], self.nodes[old_parent])
            self.graph.node[self.nodes[node]]['parent'] = e_parent
            print 'Removing edge from %s to %s' %(self.nodes[node], self.nodes[old_parent])
            if e_parent != -1:
                self.graph.add_edge(self.nodes[node], self.nodes[e_parent])
                print 'Adding edge from %s to %s' %(self.nodes[node], self.nodes[e_parent])
            else:
                print 'Node %s is now a root node' % self.nodes[node]
        except ValueError:
            pass # chose string 'same' => ignore
        try:
            weight = self.e_weight.get()
            if weight != '':
                self.graph.node['N%i'%node]['weight'] = weight # update graph to draw
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
        plt.close('all')
        #self.frame.destroy()
        #self.master.destroy()
        self.top.destroy()
        self.master.quit()
        #exit()
        #sys.exit(1)
        OutputWindow(self.master, self.g_quad(), self.g_quad(), self.info, condense=self.condense.get(), showquad=self.show_quad.get())
    
    def num_bad_vertices(self):
        '''
        Return the number of bad vertices in self.graph.
        
        Bad vertices are vertices such that -weight < degree.
        '''
        num = 0
        for node in self.nodes:
            if self.graph.node[node]['weight'] > -self.graph.degree(node):
                num += 1
        return num
    
    def g_quad(self):
        '''
        Return quadratic form (numpy array) of self.graph.
        
        Q(v,v) = weight(v)
        Q(v,w) = 1 if v, w are connected by an edge; 0 otherwise
        Thus Q is the adjacency matrix everywhere except the diagonal, and just
        the weights down the diagonal. TODO check this
        '''
        if self.num_bad_vertices() >= 2:
            raise ValueError('More than two bad vertices')
        # create adjacency matrix
        adj = nx.to_numpy_matrix(self.graph, nodelist=self.nodes, dtype=numpy.int) # order according to self.nodes
        for index, node in enumerate(self.nodes):
            adj[index, index] = self.graph.node[node]['weight']
        eigenvalues = LA.eigvalsh(adj)
        for eigen in eigenvalues:
            if eigen > 0:
                print adj
                raise ValueError('quadratric form is not negative definite')        
        return adj


if __name__ == '__main__':    
    G = nx.Graph()
    
    root = Tk()
    root.withdraw()
    #root.geometry('350x200')
    
    t=Toplevel()
    app = GraphPopup(root, G)
    #root.wait_window()
    root.wait_window()
    
    #print app.g_quad()