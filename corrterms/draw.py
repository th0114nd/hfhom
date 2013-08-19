# Caltech SURF 2013
# FILE: draw.py
# AUTHOR: Laura Shou
# MENTOR: Professor Yi Ni
# 06.21.13

'''
Draws and shades the regions for the alternating link.
Prints the Mathematica graph commands for the link.
Prints the quadratic form for the double branched cover of the link.
Press 'q' to quit Tkinter.
'''

from Tkinter import *
from knotilus_load import *
from plink_load import *
from graph_quad import *

def key_handler(event):
    '''Handle key presses.'''
    key = event.keysym
    if key == 'q': 
        quit()

def draw(c, Regions, Vertices, Intersections, Edges):
    ''''canvas 'c' '''
    for region in Regions:
        if region.angle > 0:
            region.draw(c) # draw all shaded regions (except exterior)
        else:
            print 'background shaded'

    for vertex in Vertices:
        vertex.draw(c)
    for inter in Intersections:
        inter.draw(c)    
    
    for edge in Edges:
        edge.draw(c) # draw all the edges    

def main(plink=True, filename=''):
    if plink == True:
        if filename == '':
            data = load_plink()
            all_data = make_objects(data[0],data[1],data[2],data[3],data[4],\
                                                data[5])
            Vertices, Intersections, Edges, Regions = all_data
        else:
            data = load_plink(filename)
            print 'Successfully loaded %s' % filename
            all_data = make_objects(data[0],data[1],data[2],data[3],data[4],\
                                    data[5])
            Vertices, Intersections, Edges, Regions = all_data
    else: # Knotilus
        Vertices, Intersections, Edges, Regions = load(archive, filename, save)
    Nodes=[NodeClass(i) for i in range(len(Regions))]
    t=edges_regions(Nodes,Regions)
    m=maximal_subtree(t,Nodes)
    minus=minus_maximal_subtree(t,m)
    print graph_plot(t)
    print graph_plot(maximal_subtree(t,Nodes))
    print quad_form(t,minus,Nodes)
    
    root = Tk()
    root.geometry('500x560')
    
    c = Canvas(root, width=500, height=560, bg='gray')
    c.pack()
    
    root.bind('<Key>', key_handler)    
    
    draw(c, Regions, Vertices, Intersections, Edges)
    
    root.mainloop()    
  


if __name__ == '__main__': 
    filename = False
    save = False
    plink = False
    if len(sys.argv) == 1 or len(sys.argv) > 3:
        usage()
    if sys.argv[1] == '-f' and len(sys.argv) == 3: # load filename
        filename = True
        archive = sys.argv[2]
    elif sys.argv[1] == '-s' and len(sys.argv) == 3:
        save = True
        archive = sys.argv[2]
    elif sys.argv[1] == '-p': # Plink
        plink = True
        if len(sys.argv) == 3:
            filename = sys.argv[2]
        else:
            filename = ''
    elif len(sys.argv) == 2: # don't save to file
        archive = sys.argv[1]
    else:
        usage()
    
    main(plink, filename)