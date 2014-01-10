# Caltech SURF 2013
# FILE: plink_load.py
# 09.03.13

'''
This module has functions to load Plink data and make objects (Vertices,
Intersections, Edges, Regions).

main:
Stores objects into Vertices, Intersections, Edges, and Regions.

usage: python plink_load.py [filename]
If no filename is specified, Plink editor will open.
'''

from plink_classes import *
import StringIO
import Tkinter, tkFileDialog, tkMessageBox
import numpy

#
# Check input
#
def is_closed(link):
    '''
    Return 'True' if LinkEditor object 'link' has all closed loops, 'False' if
    it has an open loop. Simpler version of method LinkEditor.warn_arcs().
    '''
    for vertex in link.Vertices:
        if vertex.is_endpoint():
            return False
    return True

def is_alternating(link):
    '''
    Return 'True' if LinkEditor object 'link' is alternating, 'False' if not.
    '''
    original = link.SnapPea_projection_file()
    try:
        link.make_alternating() # will error if not closed
    except IndexError:
        return True # for some reason Plink has an IndexError if there is a
                     # component with no crossings or intersections
                     # This only happens in 2 cases - unknot or 
                     #     split link with unknot as a component.
                     # Latter case handled by is_nonsplit
    if link.SnapPea_projection_file() == original:
        return True
    return False 

def is_nonsplit(num_comp, edges, inters):
    '''
    Return 'True' if link is non-split, 'False' otherwise.
    
    num_comp: number of components
    edges:    tuples of vertex indicies (works with output from load_plink)
    inter:    tuples of edge indices (works with output from load_plink)
    
    See http://en.wikipedia.org/wiki/Split_link
    '''
    # Algorithm:
    # form graph: nodes = knot components
    #             add edge b/w nodes iff there exists inter. b/w components
    # alternating link is non-split iff this graph is connected (BFS search)
    all_comp = [] # set of all vertices of knot (index = knot index)
    cur_comp = 0 # current component index
    for edge in edges:
        new = True # indicates first instance of matching edge with component
        index_added_to = 0
        to_delete = []
        # check if edge is already part of a component
        for index in range(len(all_comp)): # loop through all components
            comp = all_comp[index] # set of all vertices of that component
            if edge[0] in comp or edge[1] in comp:
                if new: # edge hasn't been added to any components yet
                    comp |= set([edge[0], edge[1]]) # add to set
                    all_comp[index] = comp # update
                    new = False
                    index_added_to = index
                else: # already added to previous node index_added_to
                    # combine these knots (they're connected by an edge so
                    # are part of the same knot)
                    all_comp[index_added_to] = all_comp[index_added_to].union(\
                        all_comp[index])
                    to_delete.append(index) # will delete the other
        if new: # never found a component to match, so make a new component
            all_comp.append(set([edge[0], edge[1]]))
            cur_comp += 1
        # clean up
        for itemindex in to_delete:
            del all_comp[itemindex]
    assert len(all_comp) == num_comp
    
    # form adjacency matrix
    # each node is a knot, connected by edge iff exists intersection
    adj_matrix = numpy.zeros((num_comp, num_comp), dtype=numpy.int)
    for inter in inters:
        edge1, edge2 = edges[inter[0]], edges[inter[1]]
        # find which knots edge1, edge2 are part of
        for index in range(len(all_comp)): 
            if edge1[0] in all_comp[index] or edge1[1] in all_comp[index]:
                knot1 = index
            if edge2[0] in all_comp[index] or edge2[1] in all_comp[index]:
                knot2 = index
        adj_matrix[knot1][knot2] = 1
        adj_matrix[knot2][knot1] = 1
    # got adjacency matrix
    # now do a BFS to check if it only has one component
    included = [0 for i in range(num_comp)]
    queue = [0]
    num_nodes = 0
    while queue: # nonempty
        current = queue.pop()
        num_nodes += 1
        included[current] = 1
        for index in range(num_comp):
            if adj_matrix[current][index] == 1 and included[index] == 0: 
                # (has an edge connecting node to current) and (is a new node)
                queue.append(index)
    if num_nodes == num_comp: # #nodes in connected part = total
        return True
    return False

#
# Update object properties
#
def vertex_update_edges(vertex, edge_list):
    '''
    Fills in vertex.edges, since we create all the VertexClass instances before 
    the EdgeClass instances, so can't fill in vertex.edges at creation.
    
    No output, but modifies vertex.edges.
    '''
    for edge in edge_list:
        if vertex in edge.vertices:
            vertex.edges.append(edge)

def edge_update_inter(edge, inter_list):
    '''
    Fill in edge.inter (all intersections on edge, since we make EdgeClass 
    instances before Intersections so can't fill it in then.
    
    No output, but modifies edge.inter.
    '''
    for inter in inter_list:
        if inter.over == edge or inter.under == edge:
            edge.inter.append(inter)

#
# Functions to create Regions
#
def angle_ccw_to_signed(angle):
    '''
    Given the angle measured ccw, returns the angle actually required to make
    the turn. (Left turn => negative, right turn => positive.)
        
    i.e. converts interior angle to exterior angle, with sign to identify
    it as a right (+) or left (-) turn.
    Note: this should always output +/- 2pi (exterior angle sum).
    
    This is a helper function for poly_next_edge to comptue angle attributes for
    RegionClass objects.
    '''
    angle_s = angle
    if angle_s > math.pi:  # we ended up going cw -> counts as negative angle
        angle_s -= math.pi # want to know how much it actually turned
        angle_s *= -1      # negative direction
    else:
        angle_s = math.pi - angle_s  
    return angle_s

def poly_next_edge(point, edge, old_point, knotilus=False):
    '''
    Returns tuple (next_edge, edge_dir (a vertex of the edge), angle of turn)
    (signed- right/cw => positive, left/ccw => negative)
    
    Polygon is traced out clockwise.
    
    Currently at point 'point' (Vertex or Intersection) on EdgeClass object
    'edge'. Came from point 'old_point' (Vertex or Intersection).
    
    Optional argument:
    knotilus = False => using Plink
    knotilus = True => using Knotilus (y-axis is right side up, unlike in Plink 
    (uses optional argument in plink_classes.VectorClass.angle_ccw))
    '''
    cur_vec = VectorClass(old_point.x - point.x, old_point.y - point.y)
    
    if knotilus:
        ydir = 1
    else:
        ydir = -1    

    # handle Intersections - we have 2 choices (doesn't keep going straight)
    if isinstance(point, IntersectionClass): 
        assert point == edge.inter or point in edge.inter

        # get the edge we're NOT currently on; this is our next edge
        if point.over == edge:
            other_edge = point.under
        else:
            other_edge = point.over
        
        # get 3 vectors: 1 for each direction we could go and 1 for current dir
        # all vectors have endpt at intersection, point away from intersection
        # cur_vec was already made above
        other_edge_dir1 = VectorClass(other_edge.point1.x - point.x, \
                                 other_edge.point1.y - point.y)
        other_edge_dir2 = VectorClass(other_edge.point2.x - point.x, \
                                 other_edge.point2.y - point.y)
        
        # go the direction that has the smallest angle ccw
        if cur_vec.angle_ccw(other_edge_dir1, ydir) \
           < cur_vec.angle_ccw(other_edge_dir2, ydir):
            edge_dir = other_edge.point1
            angle = cur_vec.angle_ccw(other_edge_dir1, ydir)
        else:
            edge_dir = other_edge.point2
            angle = cur_vec.angle_ccw(other_edge_dir2, ydir)
    
    # handle Vertices - just go to the next edge touching the Vertex
    else:
        if knotilus:
            assert point in edge.vertices
            assert isinstance(old_point, IntersectionClass)
            
        # get the other edge by removing the current edge
        other_edge = point.edges[:] # copy list
        other_edge.remove(edge)
        other_edge = other_edge[0]
        
        # get the edge direction, i.e. the other vertex on the edge
        edge_dir = other_edge.vertices[:] # copy list
        edge_dir.remove(point)
        edge_dir = edge_dir[0]
        
        # get the angle
        if not knotilus:
            next_pt = edge_dir
        else: 
            # knotilus edges aren't straight => use inter not endpt for next_vec
            next_pt = other_edge.inter
        next_vec = VectorClass(next_pt.x - point.x, next_pt.y - point.y)
        angle = cur_vec.angle_ccw(next_vec, ydir)
    angle = angle_ccw_to_signed(angle)
    return other_edge, edge_dir, angle

def poly_next_point(point, edge, point_dir):
    '''
    Returns the next point (Vertex or Intersection object) to go to while
    forming a region.
    
    Currently at point (Vertex or Intersection) 'point'.
    Finds the next vertex (Vertex or Intersection object) of the polygon along 
    edge 'edge', in the direction of point 'point_dir'.
    i.e. the closest point to 'point' in the correct direction.
    '''
    if isinstance(point, IntersectionClass):
        assert point in edge.inter
    else:
        assert point.index in edge.points # vertex
        
    if isinstance(point_dir, IntersectionClass):
        assert point_dir in edge.inter
    else:
        assert point_dir.index in edge.points # vertex
        
    direction = VectorClass(point_dir.x - point.x, point_dir.y - point.y)
    all_points = edge.inter + edge.vertices # all points on edge
    dir_points = [] # all points on the edge in the correct direction
    all_points.remove(point) # all the points except the current point
    for possible_point in all_points:
        if direction.is_same_dir(\
            VectorClass(possible_point.x - point.x, \
                    possible_point.y - point.y)) == True:
            dir_points.append(possible_point)
    closest_point = point_dir
    # get the closest point in the correct direction
    for test_point in dir_points:
        if point.dist(test_point) < point.dist(closest_point):
            closest_point = test_point
    assert closest_point in all_points
    return closest_point

def make_region(inter, num, knotilus=False):
    '''
    Returns the region (RegionClass object) created by IntersectionClass object
    'inter' in the direction 'num'. The region is traced out clockwise.
    
    Input:
    inter -- an IntersectionClass object 
    num -- either 0 or 1; it specifies which region to make. To make both
    regions from an intersection, run this program twice, once with num=0 and
    once with num=1.
    knotilus -- default is False (i.e. load Plink). Set to True if loading from
                the Knotilus database instead.

    Shaded region is created ccording to the coloring convention in Ozsvath and 
    Szabo, http://arxiv.org/abs/math/0309170
    '''
    angle_sum = 0
    assert num == 0 or num ==1
    vertices_list = []
    # get initial edge to go on    
    n_edge = inter.over # by shading convention

    n_point_dir = n_edge.vertices[num] # determines region 0 or region 1
    if knotilus:
        n_point = n_point_dir # flex point
    else:
        n_point = poly_next_point(inter, n_edge, n_point_dir)
    first_point = n_point # first point to go to
    prev = inter
    while 1:
        vertices_list.append(n_point)
        n_edge, n_point_dir, angle = poly_next_edge(n_point, n_edge, prev, \
                                                    knotilus)
        angle_sum += angle
        prev = n_point
        
        # get the next point
        if not knotilus:
            n_point = poly_next_point(n_point, n_edge, n_point_dir)
        else: 
            if isinstance(n_point, IntersectionClass):
                n_point = n_point_dir
                # intersection => return point_dir, since it's a flex point
            else:
                n_point = n_edge.inter
                # next point is an intersection, i.e. the one on 'edge'                 
        
        if n_point == first_point and prev == inter: # back at starting pos.
            # both conditions needed b/c if it's doing the outside region, 
            # it could come to the same intersection twice, but it needs to
            # keep going until it gets to its starting point
            break
    # last point added to vertices_list was original inter => vertices_list done
    # (first added point was first_point, not inter)
    return RegionClass(vertices_list, angle_sum)


def make_all_regions(inter_list, knotilus=False):
    '''
    Returns list of all RegionClass objects, checking for duplicates and not
    appending those.
    
    Input:
    inter_list -- the list of IntersectionClass objects to use
    knotilus -- default is False (i.e. load Plink). Set to True if loading from
                the Knotilus database instead.
    '''
    region_list = []
    for inter in inter_list:
        for i in range(2): # do it twice, once in each direction
            cur_region = make_region(inter, i, knotilus)
            # check if we've already made this region
            already_in = False
            for region in region_list:
                if cur_region == region:
                    already_in = True
                    break
            if not already_in:
                region_list.append(cur_region)
    return region_list

    
def make_objects(vertices, edges, inter, num_vert, num_edges, num_inter):
    '''
    Returns tuple (Vertices, Intersections, Edges, Regions). Each element of the
    tuple is a list of all of those types of objects.
    
    Input (these are all read off the output from Plink, like with load_plink): 
    vertices - list of tuples of each vertex
    edges - list of tuples of the edge's vertices (indexes)
    inter - list of tuples of the intersection's edges that are intersecting
            (undercrossing is first)
    num_vert - how many vertices there are
    num_edges - how many edges there are
    num_inter - how many intersections there are
    '''    
    Vertices = []      # list of all VertexClass instances
    Intersections = [] # list of all IntersectionClass instances
    Edges = []         # list of all EdgeClass instances
    Regions = []       # list of all RegionClass instances
    
    # Vertices
    for i in range(num_vert):
        Vertices.append(VertexClass(vertices[i], i))
    
    # Edges
    for j in range(num_edges):
        points = edges[j] # index of points (as tuple) in Vertices
        Edges.append(EdgeClass(j, points, Vertices[points[0]], \
                                Vertices[points[1]]))
    
    # Intersections
    for k in range(num_inter):
        cur_inter = inter[k]
        Intersections.append(IntersectionClass(Edges[inter[k][0]], \
            Edges[cur_inter[1]], \
            Edges[cur_inter[0]].intersection(Edges[cur_inter[1]])))
            # last 3rd tuple is the coords (tuple) of the intersection
            
    # update Vertex and Edge attributes
    for vertex in Vertices:
        vertex_update_edges(vertex, Edges)
    for edge in Edges:
        edge_update_inter(edge, Intersections)
    
    # Regions
    Regions = make_all_regions(Intersections)
    
    return Vertices, Intersections, Edges, Regions

#
# Plink loading
#   
def load_plink(filename='', gui=False):
    '''
    Returns the tuple (file_string, vertices, edges, inter, #vertices, #edges,
                       #intersections).
                       
    file_string is the plaintext file from Plink. If loading from a saved file,
    file_string will be empty. If drawing in Plink, file_string will be the 
    plaintext string.
    
    vertices, edges, and inter are lists of the corresponding types of objects.
    #vertices, #edges, and #intersections are the lengths of the corresponding
    lists of objects.
    
    If no input is specified, filename defaults to '', and the Plink editor
    opens so the user can draw a link. You MUST save this file.
    
    If gui=True, options will be shown in popup windows. Errors will NOT be 
    printed in a popup window. You should catch them in another program instead.
    '''
    if filename == '':
        string = True
    else:
        string = False
    
    vertices = [] # list of vertex coordinates (tuples)
    edges = []    # list of which edges to connect
    inter = []    # list of all intersections. first edge in tuple is under

    check = True # check closed and alternating
    
    if string:
        # start plink editor
        editor = plink.LinkEditor()        
        editor.window.wait_window()
        #editor.window.mainloop()
    
        # write plink lines to a string:
        file_string = editor.SnapPea_projection_file()
        
        # save file options
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        options['initialfile'] = 'plink.txt'
        
        # open the save dialog
        filename = None
        Tkinter.Tk().withdraw() # hide random window
        while not filename:
            filename = tkFileDialog.asksaveasfilename(**options)
            if filename:
                myfile = open(filename, 'w')
                print >> myfile, file_string
                myfile.close()
                break
            if tkMessageBox.askyesno('Warning',\
                    'You should save the file. Press Yes to save. ' +
                    'Press No to continue without saving. If you do not '+\
                    'save, the program will NOT be able to check that the link'\
                    + ' is closed and alternating. Results will be ' + \
                    'unpredictable. Option to show the original link will be '+\
                    'ignored.') == 0:
                check = False
                break
                
    # check closed and alternating
    if check:
        editor = plink.LinkEditor()
        editor.load(filename)
        editor.window.withdraw() # hide the window
        
        # check closed and alternating
        if not is_closed(editor):
            raise ValueError('Not all links are closed!')
        if not is_alternating(editor):
            editor.window.withdraw()
            if not gui: # command line -> print
                print 'Link projection is not alternating.'
                print 'Press [Enter] to make projection alternating' + \
                      '(will modify txt file),',
                change = raw_input('Enter q to quit. ')
                if change == '':
                    print 'Modifying file to make link alternating...'
                elif change == 'q':
                    raise ValueError('Link projection is not alternating.')
            else: # gui -> popup windows
                make_alternating = tkMessageBox.askokcancel('Warning', 
                    'Link projection is not alternating. Select OK to make ' +\
                    'link alternating (will modify txt file). ' + \
                    'Select Cancel to abort.')
                if not make_alternating:
                    raise ValueError('Link projection is not alternating.')
            editor.make_alternating()
            # overwrite file
            myfile = open(filename, 'w')
            print >> myfile, editor.SnapPea_projection_file() # overwrites
            myfile.close()
    
        # load
        try:
            knot = open(filename, 'r')
        except:
            print 'Cannot open file %s' % filename
            print 'Aborting operation; please try again'
            raise IOError('failed to open file %s' % filename)
            
    else: # check = False, loading string not file
        knot = StringIO.StringIO(file_string)
    
    knot.readline() # kill the first line
    try: # try to parse the file
        num_knots = int(knot.readline())
        
        # 1st section - number of the vertex ending each link (don't need)
        for i in range(num_knots):
            knot.readline() # just get rid of these lines
            
        # 2nd section - vertices
        num_vert = int(knot.readline())
        for j in range(num_vert):
            coord = knot.readline().split()
            vertices.append((int(coord[0]), int(coord[1])))
            
        # 3rd section - edges
        num_edges = int(knot.readline())
        for k in range(num_edges):
            edge = knot.readline().split()
            edges.append((int(edge[0]), int(edge[1])))
            
        # 4th section - intersections (tuples of which edges intersect)
        num_inter = int(knot.readline())
        for l in range(num_inter):
            cur_inter = knot.readline().split()
            inter.append((int(cur_inter[0]), int(cur_inter[1])))
        
        assert knot.readline().split()[0] == '-1'
    except:
        raise ValueError('failed to parse file. perhaps a bad file?')
    knot.close()
    # check link is non-split
    if not is_nonsplit(num_knots, edges, inter):
        if gui:
            tkMessageBox.showerror('Split link', 'Link is split, i.e. there' +\
                                   ' is a 2-sphere in its complement '+\
                                   'separating components from each other.')
        print 'Link is split'
        print 'There is a 2-sphere in its complement separating components '+\
              'from each other.'
        raise ValueError('Link is split.')
    return (vertices, edges, inter, num_vert, num_edges, num_inter, filename)

def usage():
    print 'usage: python %s filename' % sys.argv[0]
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) == 1: # no file to load => start Plink editor
        data = load_plink()
        all_data = make_objects(data[0],data[1],data[2],data[3],data[4],data[5])
        
    elif len(sys.argv) == 2: # file to load
        data = load_plink(sys.argv[1])
        print 'Successfully loaded %s' % sys.argv[1]
        all_data = make_objects(data[0],data[1],data[2],data[3],data[4],data[5])
    else:
        usage()
