# Caltech SURF 2013
# FILE: weighted_graph.py
# 09.03.13

'''
Plumbed 3-manifolds represented as negative-definite weighted forests with at 
most 2 bad vertices

Uses networkx to draw graphs and get quadratic form
'''

# It is recommended you do NOT edit the exported (saved) files by hand.
# Skipping a node number (e.g. having N3 but not N2) will raise an error.

# Known limitations
# cannot handle missing nodes
# can only delete last node

from Tkinter import *
import tkFileDialog, tkMessageBox
import networkx as nx
import matplotlib.pyplot as plt
import traceback

from gui_output import OutputWindow

import numpy
from graph_quad import symmetric, is_negative_definite
from ndqf import NDQF

class GraphPopup(Frame):
    '''
    Graph controls window. 
    
    If used in non-GUI mode, can only load graphs. (cannot create/edit/delete)
    Saving will open a window. (really meant to be used in GUI mode; non-GUI
    mode is for running tests)
    '''
    def __init__(self, master, graph=None, condense=None, show_hom=None,
                 show_quad=None, show_weighted=None, gui=True):
        self.condense = condense # variable
        self.show_hom = show_hom
        self.show_quad = show_quad # variable
        self.show_weighted = show_weighted # variable
        self.info = 'unknown' # inputinfo for the output window
        self.nodes = []
        if graph:
            self.graph = graph # networkx graph nx.Graph()
                               # Nodes are named N0, N1, N2,...
                               # Nodes have int attr. 'weight', 'parent' (index)
        else: # None
            self.graph = nx.Graph()
        self.num_nodes = 0
        self.gui = gui
        
        if not gui:
            return
        self.master = master
        self.top = Toplevel(master)
        self.top.title('Graph controls')        
        
        self.frame = self.top
        
        # New node commands
        Label(self.frame, text='New node').grid(row=1, column=0)
        Label(self.frame, text='Parent').grid(row=0, column=1)
        self.n_parent_var = IntVar()
        self.n_parent_var.set(-1) # initial value
        self.n_parent_opt = [-1]
        self.n_parentmenu = OptionMenu(self.frame, self.n_parent_var, 
                                       *self.n_parent_opt)
        self.n_parentmenu.grid(row=1, column=1)
        Label(self.frame, text='Weight').grid(row=0, column=2)
        self.n_weight = Entry(self.frame, width=4)
        self.n_weight.grid(row=1, column=2)
        Button(self.frame, text='Create', command=self.create_node).grid(row=1,
                                                                    column=3)
        
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
        self.e_nodemenu = OptionMenu(self.frame, self.e_node_var, 
                                     *self.e_node_opt)
        self.e_nodemenu.grid(row=4, column=1)
        # Select a new parent
        self.e_parent_opt = ['same',-1,0]
        self.e_parentmenu = OptionMenu(self.frame, self.e_parent_var, 
                                       *self.e_parent_opt)
        self.e_parentmenu.grid(row=4, column=2)
        self.e_weight = Entry(self.frame, width=4)
        self.e_weight.grid(row=4, column=3)
        
        Button(self.frame, text='Done', command=self.edit_node).grid(row=4, 
                                                                     column=4)
        separator = Frame(self.frame, height=2, bd=1, relief=SUNKEN)
        separator.grid(row=5, sticky='we', padx=5, pady=5, columnspan=5)
        
        # Delete last node
        Label(self.frame, text='Delete last node').grid(row=6, column=0)
        self.del_node = Label(self.frame, text='Node #%i'%self.num_nodes)
        self.del_node.grid(row=6, column=1) 
        Button(self.frame, text='Delete', command=self.delete_node).grid(row=6,
                                                                       column=4)
        
        separator = Frame(self.frame, height=2, bd=1, relief=SUNKEN)
        separator.grid(row=7, sticky='we', padx=5, pady=5, columnspan=5)
        
        # File buttons
        Button(self.frame, text='Draw graph', command=self.update_graph).grid(\
            row=9, column=0)
        Button(self.frame, text='Save as', command=self.save).grid(row=9, 
                                                                   column=1)
        Button(self.frame, text='Load', command=self.load).grid(row=9, column=2)
        Button(self.frame, text='Done/compute', command=self.close).grid(row=9,
                                                                    column=3)
        Button(self.frame, text='Cancel', command=self.cancel).grid(row=9, 
                                                                    column=4)
        
        #self.update_graph() # show matplotlib drawing screen
        
    def update_graph(self):
        '''Redraw graph in matplotlib.pyplot.'''
        plt.clf() # erase figure
        labels = dict((n, '%s,%s' %(n,a['weight'])) \
                      for n,a in self.graph.nodes(data=True))
        nx.draw_graphviz(self.graph, labels=labels, node_size=700, width=3, 
                         alpha=0.7)
        plt.show()
    
    def missing_nodes(self):
        '''
        Return list of indices of missing nodes, using highest numbered node as
        the total number of nodes.
        
        By 'missing a node', mean that node numbering skips from, eg. N1 to N3,
        with N2 missing.
        
        Raises error if any node indices aren't integers or are negative ints.
        '''
        nodes = self.graph.nodes(data=False)
        num_nodes = 0
        indices = []
        for node in nodes:
            indices.append(int(node[1:])) # node is Nk, node[1:] gives int k
            assert int(node[1:]) >= 0
            if int(node[1:]) > num_nodes:
                num_nodes = int(node[1:])
        return set(range(num_nodes)).difference(set(indices))
    
    def create_node(self):
        '''
        Create a new node from the "Create New" options.
        A parent index of -1 means it is a root node (no parent).
        Only works when used with the GUI.
        '''
        if not self.gui:
            print 'Cannot create nodes in non-GUI mode'
            return
        try:
            n_weight = int(self.n_weight.get())
        except:
            tkMessageBox.showerror('Weight', 'No data for weight or not an int')
            raise ValueError('no data for weight or not an int')
        new_name = 'N%i' % self.num_nodes
        parent_index = self.n_parent_var.get()
        self.graph.add_node(new_name, parent=parent_index, weight=n_weight)
        self.nodes.append(new_name)
        if parent_index != -1: # not a root node
            # Create edge to parent
            parent_node = self.nodes[parent_index]
            self.graph.add_edge(parent_node, new_name)
        # update New node dropdown menu (add node just created)
        self.n_parent_opt.append(self.num_nodes)
        self.n_parentmenu.destroy()
        self.n_parentmenu = OptionMenu(self.frame, self.n_parent_var, 
                                       *self.n_parent_opt)
        self.n_parent_var.set(self.num_nodes) # default parent is newest node
        self.n_parentmenu.grid(row=1, column=1)
        # update Edit dropdown menu        
        if self.num_nodes != 0:
            self.e_node_opt.append(self.num_nodes)
            self.e_nodemenu.destroy()
            self.e_nodemenu = OptionMenu(self.frame, self.e_node_var, 
                                         *self.e_node_opt)
            self.e_nodemenu.grid(row=4, column=1)
            
            self.e_parent_opt.append(self.num_nodes)
            self.e_parentmenu.destroy()
            self.e_parentmenu = OptionMenu(self.frame, self.e_parent_var, 
                                           *self.e_parent_opt)
            self.e_parentmenu.grid(row=4, column=2)
        self.num_nodes += 1
        self.update_graph()
        # update Delete menu
        self.del_node.destroy()
        self.del_node = Label(self.frame, text='Node #%i'%(self.num_nodes-1))
        self.del_node.grid(row=6, column=1)        
    
    def edit_node(self):
        '''Edit node according to "Edit node" options.'''
        if not self.gui:
            print 'Cannot edit nodes in non-GUI mode'
            return
        if self.num_nodes == 0:
            tkMessageBox.showerror('No nodes', 
                                   'No nodes to edit. You must create a node.')
            raise ValueError('no nodes to edit')
        node = self.e_node_var.get()
        old_parent = self.graph.node[self.nodes[node]]['parent']
        # Edit parent node
        try: 
            e_parent = self.e_parent_var.get() # may not be an int ('same')
            # make sure don't choose self as new parent (self loop)
            if node == e_parent:
                tkMessageBox.showwarning('Parent', 
                                         'Cannot choose self as parent')
                return
            # update parent attribute
            self.graph.node[self.nodes[node]]['parent'] = e_parent
            # update edges
            if old_parent != -1: # wasn't a root node
                self.graph.remove_edge(self.nodes[node], self.nodes[old_parent])
                print 'Removing edge from %s to %s' %(self.nodes[node], 
                                                      self.nodes[old_parent])
            if e_parent != -1: # not making node a root node
                self.graph.add_edge(self.nodes[node], self.nodes[e_parent])
                print 'Adding edge from %s to %s' %(self.nodes[node], 
                                                    self.nodes[e_parent])
            else:
                print 'Node %s is now a root node' % self.nodes[node]
        except ValueError:
            print 'Not changing parent' # chose string 'same' => ignore
        # Edit weight
        try:
            weight = self.e_weight.get()
            if weight != '':
                self.graph.node['N%i'%node]['weight'] = int(weight)
        except ValueError:
            tkMessageBox.showerror('Invalid weight', 'Invalid weight.')
            raise ValueError('Invalid weight')
        
        self.update_graph() # redraw graph
    
    def delete_node(self):
        '''Delete the last node.'''
        if not self.gui:
            print 'Cannot delete nodes in non-GUI mode'
            return
        if self.num_nodes == 0:
            tkMessageBox.showwarning('No nodes', 'Nothing to delete')
            return
        self.graph.remove_node('N%i'%(self.num_nodes-1))
        print 'Deleted node %i'%(self.num_nodes-1)
        # update Create menu
        self.n_parent_opt.pop()
        self.n_parentmenu.destroy()
        self.n_parentmenu = OptionMenu(self.frame, self.n_parent_var, 
                                       *self.n_parent_opt)
        self.n_parent_var.set(self.num_nodes-2) # default parent is newest node
        self.n_parentmenu.grid(row=1, column=1)        
        # update Edit menu
        self.e_node_opt.pop()
        self.e_nodemenu.destroy()
        self.e_nodemenu = OptionMenu(self.frame, self.e_node_var, 
                                     *self.e_node_opt)
        self.e_nodemenu.grid(row=4, column=1)
        
        self.e_parent_opt.pop()
        self.e_parentmenu.destroy()
        self.e_parentmenu = OptionMenu(self.frame, self.e_parent_var, 
                                       *self.e_parent_opt)
        self.e_parentmenu.grid(row=4, column=2)        
        # update Delete menu
        self.del_node.destroy()
        self.del_node = Label(self.frame, text='Node #%i'%(self.num_nodes-2))
        self.del_node.grid(row=6, column=1)
        self.num_nodes -= 1
        self.nodes.pop()
        
        self.update_graph()
    
    def save(self):
        '''Save to file as adjacency list and node data.'''
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

    def load(self, filename=None):
        '''
        Load adjacency list and data from file. This will remove the graph 
        created by the editor in the current session.
        
        Lines at the beginning starting with # are ignored. 
        The adjacency list for the matrix is first.
        The line following DATA that contains a list of all the nodes with 
        attributes must be on a single line (no line breaks). 
        It should be the output of graph.nodes(data=True).
        Lines after this line are ignored.
        
        Example file:
        #weighted_graph.py
        # GMT Fri Aug 16 22:24:35 2013
        #
        N0 N1 N2 N3
        N1 
        N2 
        N3 

        DATA
        [('N0', {'weight': -3, 'parent': -1}), ('N1', {'weight': -3, 'parent': 
        0}), ('N2', {'weight': -3, 'parent': 0}), ('N3', {'weight': -3, 
        'parent': 0})]
        '''
        if not filename: 
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
            if self.gui:
                tkMessageBox.showwarning('Open file',
                                         'Cannot open file %s.' %filename \
                                    +'Aborting operation; please try again.')
            raise IOError('failed to open file')
        # get the adjacency list
        adjlist = [] # list of strings
        try:
            while 1:
                line = adjfile.readline()
                if not line: # 'DATA' line should come before EOF
                    raise IOError('failed to load - possibly no graph data')
                if line[:4] == 'DATA' or line[:4] == 'data':
                    break
                if line[0] == '#' or line == '' or line == '\n': # skip
                    continue
                adjlist.append(line[:-1]) # don't want \n char
            self.graph = nx.parse_adjlist(adjlist) # got graph
            self.num_nodes = len(self.graph.nodes(data=False))            
            if not is_forest(self.graph):
                raise ValueError('not a forest (disjoint union of trees)')
            missing_nodes = self.missing_nodes()
            if missing_nodes != set([]):
                raise ValueError('missing node(s)')
            # get the node data- must be preceded by a line starting with 'DATA'
            while 1:
                node_data = adjfile.readline()
                if not node_data: # EOF
                    raise IOError('no data')
                if node_data != '' and node_data != '\n':
                    break
            # use eval convert node_data (string) to list; make sure is a list
            if node_data.strip()[0] != '[' or node_data.strip()[-1] != ']':
                raise ValueError('cannot parse data')
            # add node attributes (weight, parent)
            for node in eval(node_data):
                for attr in node[1].keys():
                    self.graph.node[node[0]][attr] = node[1][attr] 
                    # node[1] is a dict of attr
            # update self.nodes (keep in order)
            self.nodes = []
            for index in range(self.num_nodes):
                self.nodes.append('N%i' % index)
        except Exception as error:
            if self.gui:
                tkMessageBox.showwarning('Loading', 'Loading failed - %s%s\n%s'\
                                %(type(error),filename, traceback.format_exc()))
            print traceback.print_exc()
            return
        # update graph control options
        if self.gui:
            self.n_parent_opt = range(-1, self.num_nodes)
            self.n_parentmenu = OptionMenu(self.frame, self.n_parent_var, 
                                           *self.n_parent_opt)
            self.n_parentmenu.grid(row=1, column=1)
            self.e_node_opt = range(self.num_nodes)
            self.e_nodemenu = OptionMenu(self.frame, self.e_node_var, 
                                         *self.e_node_opt)        
            self.e_nodemenu.grid(row=4, column=1)        
            self.e_parent_opt = ['same']
            self.e_parent_opt.extend(range(-1, self.num_nodes))
            self.e_parentmenu = OptionMenu(self.frame, self.e_parent_var, 
                                           *self.e_parent_opt)                
            self.e_parentmenu.grid(row=4, column=2)
            
            self.del_node.destroy()
            self.del_node = Label(self.frame,text='Node #%i'%(self.num_nodes-1))
            self.del_node.grid(row=6, column=1)

            self.update_graph()
        print 'Graph data successfully loaded from %s' % filename        
        
    def close(self):
        '''Close and output correction terms.'''
        if not self.gui:
            print 'Nothing to close'
            return
        if self.num_nodes == 0:
            tkMessageBox.showerror('No nodes', 
                                   'No graph drawn. Closing editor.')
            self.top.destroy()
            return
        self.save()        
        quad = g_quad(self.graph, self.nodes)
        quadform = NDQF(quad)
        corr = quadform.correction_terms()
        struct = quadform.group.struct()
        
        self.top.destroy()
        #self.master.quit()
        if not self.show_weighted.get():
            plt.close('all')            
        OutputWindow(self.master, corr, struct, quad, self.info,
                     condense=self.condense.get(),
                     showquad=self.show_quad.get(),
                     showhom=self.show_hom.get())
    
    def cancel(self):
        '''Exit program without computing correction terms.'''
        if not self.gui:
            print 'Nothing to close'
            return
        print 'Quitting...'
        plt.close('all')
        self.top.destroy()
        #self.master.quit()

def is_forest(graph):
    '''
    Return True if graph is a forest (disjoint union of trees), otherwise 
    False.
    
    A graph is a forest iff #nodes = #edges + #components.
    e.g. see http://www-math.mit.edu/~sassaf/courses/314/solp2.pdf
    '''
    if len(graph.nodes(data=False)) == graph.number_of_edges() + \
                                        nx.number_connected_components(graph):
        return True
    return False

def num_bad_vertices(graph, node_list):
    '''
    Return the number of bad vertices in networkx graph 'graph'.
    
    Bad vertices are vertices such that -weight < degree. 
    'node_list' is a list of the names of all the nodes to check.
    '''
    num = 0
    for node in node_list:
        assert type(graph.node[node]['weight']) is int
        assert type(graph.degree(node)) is int
        if graph.node[node]['weight'] > -graph.degree(node):
            num += 1
    return num
    
def g_quad(graph, node_list, gui=True):
    '''
    Return quadratic form (numpy array) of networkx graph 'graph', ordered
    according to the node names in 'node_list'.
    
    Q(v,v) = weight(v)
    Q(v,w) = 1 if v, w are connected by an edge; 0 otherwise
    Thus Q is the adjacency matrix everywhere except the diagonal, and just
    the weights down the diagonal.
    '''
    assert len(node_list) == len(graph.nodes(data=False))
    assert is_forest(graph)
    num_bad = num_bad_vertices(graph, node_list)
    if num_bad > 2:
        if gui:
            tkMessageBox.showwarning('Bad vertices', 
                          'More than two bad vertices. (There are %i.)'%num_bad)
        raise ValueError('More than two bad vertices. (There are %i.)'%num_bad)
    # create adjacency matrix, ordered according to node_list
    adj = nx.to_numpy_matrix(graph, nodelist=node_list, dtype=numpy.int)
    for index, node in enumerate(node_list): # change diagonal
        adj[index, index] = graph.node[node]['weight']
    if not is_negative_definite(adj):
        if gui:
            tkMessageBox.showwarning('Quadratic form', 
                                     'Quadratic form is not negative definite')
        print adj
        raise ValueError('quadratric form is not negative definite')        
    return adj


if __name__ == '__main__':
    # this file really intended to be used with gui.py, not by itself
    print 'Do NOT use Done/Compute. Use Cancel instead.'
    print 'Then close the root tk window.'
    G = nx.Graph()
    
    root = Tk()
    #root.withdraw()
    
    app = GraphPopup(root, G)
    root.wait_window()
    
    print g_quad(app.graph, app.nodes)