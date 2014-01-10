# Caltech SURF 2013
# FILE: knotilus_load.py
# 08.22.13

'''
This module has functions to load Knotilus data and make objects (Vertices, 
Edges, Intersections, Regions).

It imports methods from plink_load.py.


main:
usage: python knotilus_load.py [-s] archive_num
OR     python knotilus_load.py -f filename

Optional argument -s: save the downloaded file for archive_num as
                      'archive_num.txt'
-f argument: load the filename 'filename', don't download from the database
If 'filename' does not exist, prompts to download from Knotilus.

'''

import plink, StringIO
from knotilus_classes import *
from knotilus_download import *
from plink_load import angle_ccw_to_signed, vertex_update_edges, make_region,\
     make_all_regions, poly_next_edge

class BadFileError(Exception):
    pass

#
# Knotilus loading
#
def get_coords(coords):
    '''
    Take a string 'coords' like '(351.581,110.369,1)' and return an array of the 
    the coordinates as a tuple (first 2 numbers) and an integer for the third 
    number. Eg. [(351.581,110.369),1]
    '''
    # get rid of \n, (, and ), then split by ,
    coords = coords.strip().strip('(').strip(')').split(',')
    coords_tuple = (float(coords[0]), float(coords[1]))
    third_coord = int(coords[2]) # -1 or 1 for intersection, 0 for flex pt    
    return [coords_tuple, third_coord]

def load_knotilus(filename, string=False, gui=False):
    '''
    Returns tuple (vertices, edges, inter).
    vertices: a list of the coordinates of the vertices
        (coord1, coord2)
    edges: a list of lists of the form 
        [intersection_index, (1st_flexpt_index, 2nd_flexpt_index)]
    inter: a list of lists of the form
        [(coord1, coord2), (seg1, seg2), (seg3, seg4)],
        where (seg1, seg2) are segment indices for the under edge 
        and (seg3, seg4) are segment indices for the over edge.
        
    If string=False, loads the data in the file 'filename', which should be 
    downloaded from Knotilus as a plaintext file.
    
    If string=True, 'filename' should be a string that is the plaintext file
    from Knotilus. Then loads data from the string 'filename' (which is not
    a filename; it's the contents of a plaintext file from Knotilus).
    '''
    vertices = [] # list of vertex coordinates (2-tuples)
    edges = []    # list of edges
    inter = []    # list of intersections 
    # see docstring (under output) for more description
    
    if not string: # load file
        try:
            knot = open(filename, 'r')
        except:
            if not gui:
                print 'Cannot open file %s' % filename
                print 'Aborting operation; please try again'
                raise IOError('failed to open file')
            else: # gui -> messagebox
                tkMessageBox.showwarning('Open file','Cannot open file %s.' \
                                         %filename + \
                                        'Aborting operation; please try again.')
                raise IOError('failed to open file')            
    else: # open string for reading like file
        knot = StringIO.StringIO(filename)
    
    try:
        for i in range(4):
            line = knot.readline() # kill off the intro lines
            assert line != ''
        assert line == 'Embedding for: Component 1\n'
        
        prev_inter_third = 0 # prev intersection's 3rd coord, +/-1 (over/under)
        # will be used to check alternating
        
        prev_flex_index = -1 # prev flex point's index. This is used for 'edges'.
        # the 1st edge of each link component has prev_flex_point -1 (the last 
        # pt), but this value will be stored as a positive number (#vertices-1),
        # where #vertices is the number of vertices for that component.
        
        segment = -1 # keep track of segment number. increases by 2 each time
        # first segment = 0, last segment = -1 mod #segments
        
        cur_num_vert = 0 # current component's # of vertices (not intersections)
        cur_start_index = 0 # current component's first vertex's index
        
        # loop through all points in the file
        while 1:
            coords = knot.readline()
            if not coords: # EOF
                edges[cur_start_index][1][0] = cur_start_index + cur_num_vert-1
                break
            if coords[0] != '(': # signifies end of link's vertices
                edges[cur_start_index][1][0] = cur_start_index + cur_num_vert-1
                cur_start_index += cur_num_vert # moving on to next component
                prev_inter_third = 0 # reset alternating check
                cur_num_vert = 0 # reset number of vertices for this component
                continue # skip loop, start over
            coords_tuple, third_coord = get_coords(coords)       
            
            #
            # Intersections
            # eg: ((coord1, coord2), (1,2), (7,8))
            # represented as coordintates (coord1, coord2), followed by tuples for
            # each edge. eg. (1,2) is the edge with segments 1 and 2.
            if abs(third_coord) == 1: # intersection
                
                # check alternating link
                if abs(prev_inter_third) == 1 and \
                   third_coord != -prev_inter_third:
                    raise ValueError('link is not alternating')
                prev_inter_third = third_coord         
                
                # check if we've already passed this intersection
                new = True
                index = 0 # the ith intersection
                for intersection in inter:
                    if intersection[0] == coords_tuple:
                        new = False
                        break
                    index += 1
                
                if new == True: # new intersection => add it
                    # [coors_tuple, under, over]
                    if third_coord == -1: # under
                        inter.append([coords_tuple, (segment, segment+1), 0])
                    else:
                        inter.append([coords_tuple, 0, (segment, segment+1)])
                        # note: only coords and one edge pair are known
                        
                else: # already passed intersection
                    if third_coord == -1: # under
                        assert(inter[index][1] == 0), 'corrupted file'
                        # ^ can't have both crossings be undercrossings
                        inter[index][1] = (segment, segment+1) # add 2nd edge
                    else: # over
                        assert(inter[index][2] == 0), 'corrupted file'
                        inter[index][2] = (segment, segment+1)
                        
                #
                # Edges (one edge per intersection occurance)
                edges.append([index, [prev_flex_index, prev_flex_index+1]])
                # prev_flex_index, prev_flex_index+1 give indices for flex pts 
                # of edges. At the end of a specific component, will need to
                # modify the first edge for that component: 
                # [-1, first_flex_index] needs to be 
                # [last_flex_index, first_flex_index]
                segment += 2
                
            #                 
            # Flex points (vertices): third_coord = 0
            #
            else:
                vertices.append(coords_tuple)
                prev_flex_index += 1
                cur_num_vert += 1
    
        knot.close()
        
        assert(len(vertices) == len(edges))
        assert(len(vertices) == 2*len(inter)) # each intersection visited twice,
                                            # but counted once
    except:
        if not gui: # command line
            raise ValueError('failed to parse file. perhaps a bad file?')
        else: # gui
            tkMessageBox.showerror('Parsing file', 
                                   'Failed to parse file. Perhaps a bad file?')
            raise ValueError('failed to parse file.')    
    return (vertices, edges, inter)

#
# Knotilus make objects
#      
def make_objects(vertices, edges, inter):
    '''
    Returns a tuple (Vertices, Intersections, Edges, Regions). Each element of
    the tuple is a list of all the corresponding objects of that type.
    
    Input (output from function 'load_knotilus')
    vertices - list of coordinate 2-tuple for each vertex, eg. (coord1, coord2)
    edges - list of lists, each of form 
            [intersection_index, (1st_flexpt_index, 2nd_flexpt_index)]
    inter - list of lists, each of the form
            [(coord1, coord2), (seg1, seg2), (seg3, seg4)],
            where (seg1, seg2) are segment indices for the under edge 
            and (seg3, seg4) are segment indices for the over edge.
    '''    
    Vertices = []      # list of VertexClass objects
    Intersections = [] # list of IntersectionClass objects
    Edges = []         # list of EdgeClass objects
    Regions = []       # list of RegionClass objects    

    # Vertices
    for i in range(len(vertices)):
        Vertices.append(VertexClass(vertices[i], i))
    
    # KEdges
    for j in range(len(edges)):
        points = edges[j][1] # tuple - indices for flex points
        new_edge = KEdgeClass(j, Vertices[points[0]], Vertices[points[1]], \
                              points, edges[j][0])
            # will need to update self.inter later - edges[j][0] is an index, 
            # but needs to be an Intersection object        
        Edges.append(new_edge)

    # Intersections
    for k in range(len(inter)):
        # can get edge index for the intersection by taking 2nd segment index, 
        # and dividing by 2 (edges increase by 1, segments increase by 2)
        # eg. (1,2) is the 1st (after the 0th) edge
        Intersections.append(IntersectionClass(Edges[inter[k][1][1]/2], \
                                    Edges[inter[k][2][1]/2], inter[k][0]))
        
    # update vertex and edge attributes
    for vertex in Vertices:
        vertex_update_edges(vertex, Edges) # update vertex.edges
    for edge in Edges:
        edge.inter = Intersections[edge.inter] # index -> Intersection object
        
    # Regions
    Regions = make_all_regions(Intersections, True)
    
    return Vertices, Intersections, Edges, Regions

def load(archive, filename=False, save=False, gui=False):
    '''
    Loads data and returns tuple (Vertices, Intersections, Edges, Regions), 
    of all objects from the data.
    
    If 'filename=True' but file 'archive' does not exist, prompts to download 
    from Knotilus. If downloading and 'save=True', will save to file. 
    '''
    if filename:
        while 1:
            try:
                data = load_knotilus(archive)
                return make_objects(data[0], data[1], data[2])
            except IOError: # file doesn't exist (not a problem with GUI)
                print "'%s'does not exist in the current directory." % archive
                answer = raw_input('Download from Knotilus? [y/n] ')            
                while 1: # do this until get a y/n
                    if answer == 'y': # download from knotilus
                        # check requested file has form ax-b-c.txt or ax-b-c
                        # if yes, download ax-b-c, save as ax-b-c.txt
                        if valid_archive_form(archive.split('.txt')[0]):
                            download_save(archive.split('.txt')[0])
                            # make sure '.txt' is the extension of 'archive'
                            if archive[-4:] != '.txt':
                                archive = archive + '.txt'
                            print 'Downloaded successfully to %s' % archive
                            break 
                            # goes back to outer while loop;loads data from file
                        else: # not a valid archive number
                            print 'could not determine archive number'
                            while 1:
                                archive = raw_input(\
                        'Input a valid archive number, or input n to quit: ')
                                if archive == 'n':
                                    sys.exit(1)
                                if valid_archive_form(archive):
                                    download_save(archive)
                                    break
                                else:
                                    print \
        'Not valid: Archive number must be of the form ax-b-c, for a,b,c ints'
                    elif answer == 'n':
                        print 'Quitting...'
                        sys.exit(1)
                    else: # not a y or n
                        answer = raw_input('Enter y or n: ')
    elif save:
        download_save(archive)
        print 'Successfully saved to %s.txt' % archive
        return load(archive + '.txt', filename=True, save=False) # load file
    else: # don't save to file
        data = load_knotilus(get_plaintext(archive,gui), True) # True=>stringIO
        return make_objects(data[0], data[1], data[2])

def usage():
    print 'usage: python %s [-s] archive_num' % sys.argv[0]
    print 'OR     python %s -f filename'
    sys.exit(1)

if __name__ == '__main__':
    filename = False
    save = False
    if len(sys.argv) == 1 or len(sys.argv) > 3:
        usage()
    if sys.argv[1] == '-f' and len(sys.argv) == 3: # load filename
        filename = True
        archive = sys.argv[2]
    elif sys.argv[1] == '-s' and len(sys.argv) == 3:
        save = True
        archive = sys.argv[2]
    elif len(sys.argv) == 2: # don't save to file
        archive = sys.argv[1]
    else:
        usage()
    all_data = load(archive, filename, save)