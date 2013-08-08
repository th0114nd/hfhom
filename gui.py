# Caltech SURF 2013
# FILE: gui.py
# 08.06.13

'''
Main user interface for entering link data.
'''

# main/start window dimensions
windowx = 450
windowy = 475

import traceback
from Tkinter import *
import tkFileDialog, tkMessageBox, ImageTk, Image, tkFont, plink
from graph_quad import *
from knotilus_download import valid_archive_form, browser_link
from seifert import s_quad_form, correct_form

def regions_to_quad(regions):
    '''input list of regions, output numpy array for quadratic form'''
    Nodes = [NodeClass(i) for i in range(len(regions))]
    t = edges_regions(Nodes,regions)
    m = maximal_subtree(t, Nodes)
    minus = minus_maximal_subtree(t, m)
    return quad_form(t, minus, Nodes)

class StartWindow(Frame):
    def __init__(self, master):        
        self.master = master
        self.master.title('Hfhom')
        
        # http://effbot.org/tkinterbook/menu.htm
        # make menu
        self.menubar = Menu(root)
        # File
        filemenu = Menu(self.menubar, tearoff=0)
        
        # File > New options
        filemenu.add_command(label='Exit', command=root.quit)
        self.menubar.add_cascade(label='File', menu=filemenu)
    
        # View
        #viewmenu = Menu(self.menubar, tearoff=0)
        #self.menubar.add_cascade(label='View', menu=viewmenu)

        # Help
        helpmenu = Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label='Instructions', command=self.help)
        helpmenu.add_command(label='About Hfhom...', command=self.about)
        self.menubar.add_cascade(label='Help', menu=helpmenu)
        
        master.config(menu=self.menubar)
        
        # Title
        Label(master, text='Heegaard Floer Correction Terms', \
              font=tkFont.Font(size=12)).grid(row=0, sticky='w', columnspan=4)
        
        # Banner image
        image = Image.open('banner_small.png')
        knotimage = ImageTk.PhotoImage(image)
        
        bannerlabel = Label(image=knotimage)
        bannerlabel.image = knotimage # keep reference (else garbage collected)
        bannerlabel.grid(row=1, sticky='w', columnspan=4)
        
        # Subtitle
        #Label(master, text='Actually just quadratic form...').pack(anchor='w')
        
        # Options
        Label(master, text='Show:').grid(sticky='w')
        show_quad = IntVar()
        show_link = IntVar()
        show_shaded = IntVar()
        show_graph = IntVar()
        self.condensed = IntVar()
        
        q = Checkbutton(master, text='quadratic form', variable=show_quad)
        q.grid(row=2, column=1, sticky='w')
        
        Label(master, text='Knotilus, Plink:').grid(row=3, column=0, sticky='w')
        Checkbutton(master, text='original link', variable=show_link).grid(\
            row=3, column=1, sticky='w')
        Checkbutton(master, text='shaded link', variable=show_shaded).grid(\
            row=3, column=2, sticky='w')
        g = Checkbutton(master, text='graph commands', variable=show_graph)
        g.grid(row=3, column=3, sticky='w')        
        
        Checkbutton(master, text='condense correction terms', \
                    variable=self.condensed, \
                    command=lambda: self.disable_checkboxes([q,g])).grid(\
                        row=2, column=2, sticky='w', columnspan=2)
        
        # useful stuff
        # font for Knotilus, Plink, Seifert headers
        section_font = tkFont.Font(size=9, weight='bold')      
        knotilus = KnotilusBox(master, section_font, self.condensed, show_quad,\
                               show_link, show_shaded, show_graph)
        plink = PlinkBox(master, section_font, self.condensed, show_quad, \
                         show_link, show_shaded, show_graph)
        seifert = SeifertBox(master, section_font, self.condensed, show_quad)
        
        # Banner image again        
        bannerlabel2 = Label(image=knotimage)
        bannerlabel2.image = knotimage # keep reference (else garbage collected)
        bannerlabel2.grid(sticky='w', columnspan=4)  
        
        #canvas = Canvas(frame, bg="black", width=500, height=500)
        #canvas.pack()        
        #canvas.create_image(150, 150, image=knotimage)
        #canvas.pack()
            
        #frame.pack()
        
    def disable_checkboxes(self, list_disable):
        '''Disable checkboxes in list 'list_disable'.'''
        if self.condensed.get():
            for box in list_disable:
                box.configure(state=DISABLED)
        else:
            for box in list_disable:
                box.configure(state=NORMAL)
    
    def about(self):
        AboutWindow(self.master)
    
    def help(self):
        print 'help'    


class KnotilusBox(object):
    '''Enter Knotilus archive number'''
    def __init__(self, master, section_font, condense, show_quad, show_link,\
                 show_shaded, show_graph):
        self.master = master
        self.show_quad = show_quad
        self.show_link = show_link
        self.show_shaded = show_shaded
        self.archive_num = None
        self.show_graph = show_graph
        self.condense = condense # to show single line output
        
        kframe = LabelFrame(master, text='Knotilus archive', font=section_font,\
                            padx=5, pady=5)
        
        # new Knotilus (download from database)
        text = Label(kframe, text='Enter archive number (ax-b-c).')
        text.grid(row=0, column=0)
        self.entry = Entry(kframe)
        self.entry.grid(row=0, column=1)        
        Button(kframe, text='Go', command=self.knotilus).grid(row=0, column=2)  
        '''
        text = Label(kframe, text='Enter starting archive number,\n' + \
        'of the form ax-b-c, e.g. 6x-2-1')
        text.grid(row=0, column=0)
        self.entry = Entry(kframe, width=12)
        self.entry.grid(row=0, column=1)
        Label(kframe, text='#links').grid(row=0, column=2)
        self.num_links = Entry(kframe, width=3)        
        self.num_links.grid(row=0, column=3)
        self.num_links.insert(0,1) # default value
        Button(kframe, text='Go', command=self.knotilus).grid(row=0, column=4)
        '''
        
        # load Knotilus file
        text2 = Label(kframe, text='Open saved Knotilus file')
        text2.grid(row=1, column=0)
        Button(kframe, text='Open', command=self.k_load_file).grid(\
            row=1, column=1, sticky='w', columnspan=3)
      
        kframe.grid(padx=15, pady=10, sticky='w', column=0, columnspan=4)
            
    def knotilus(self):
        # will run loading and correction terms later... TODO
        self.archive_num = self.entry.get()
        if not valid_archive_form(self.archive_num):
            tkMessageBox.showwarning('Invalid archive form.\n',\
                    'Archive number must have form ax-b-c, for ints a,b,c. ' +\
                    'Please try again.')
        else:
            data = load(self.archive_num, False, False, gui=True)
            regions = data[3]
            
        if self.show_shaded.get():
            vie = (data[0], data[1], data[2]) # Vertices, Intersections, Edges
        else:
            vie = None
        self.k_output(regions, vie, self.archive_num)

            
    def k_load_file(self):
        '''select file to load'''
        # open file options
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        self.filename = tkFileDialog.askopenfilename(**options)

        if self.filename == '': # canceled
            return
        
        try:
            data = load(self.filename, True, False)
            regions = data[3]
        except Exception as error:
            tkMessageBox.showwarning('Loading', \
                                     'Loading failed - %s%s'%(type(error),\
                                                              self.filename))
            print traceback.print_exc()
            return
        
        if self.show_shaded.get():
            vie = (data[0], data[1], data[2]) # Vertices, Intersections, Edges
        else:
            vie = None
        self.k_output(regions, vie, self.filename)
    
    def k_output(self, regions, vie, inputinfo):
        quad = regions_to_quad(regions)
        
        if self.show_link.get():
            if not self.archive_num: # loaded file
                # attempt to use filename to load original link
                # e.g. '6x-1-1.txt' or '6x-1-1' will work
                archive_num = self.filename.split('/')[-1].split('.txt')[0]
                # FIXME this is only going to work on linux...
                if valid_archive_form(archive_num):
                    browser_link(archive_num)
                # else ignore and do nothing
            else:
                browser_link(self.archive_num) # open browser to original link
        
        # TODO: ouptut correction terms not quad
        if self.condense.get():
            self.output = OutputWindow(self.master, quad, quad, inputinfo, \
                                       condense=True)
        else:
            self.output = OutputWindow(self.master, quad, quad, inputinfo, \
                                       showquad=self.show_quad.get(), \
                                       showgraph=self.show_graph.get(), \
                                       regions=regions)
        #self.master.wait_window(self.output.top)           
        
        if self.show_shaded.get():
            ShadedLinkWindow(self.master, regions, vie[0], vie[1], vie[2], \
                             inputinfo, flip=True) 
            # opens window to show shaded link
            # flips coordinates so drawn right side up (Tkinter y-axis reversed)

class PlinkBox(object):
    '''Plink loading'''
    def __init__(self, master, section_font, condense, show_quad, show_link,\
                 show_shaded, show_graph):
        self.master = master
        self.show_quad = show_quad
        self.show_link = show_link
        self.show_shaded = show_shaded     
        self.show_graph = show_graph
        self.condense = condense
        
        pframe = LabelFrame(master, text='Plink/SnapPy', font=section_font, \
                            padx=5, pady=5)
        
        # new Plink???
        text = Label(pframe, text='Create a new Plink/SnapPy file.')
        text.grid(row=0, column=0)
        Button(pframe, text='Create New', command=self.new_plink).grid(row=0, \
                                                                       column=1)
        
        # load Plink file
        text2 = Label(pframe, text='Load existing Plink file')
        text2.grid(row=1, column=0)
        Button(pframe, text='Open', command=self.p_load_file).grid(row=1, \
                                                        column=1, sticky='W')
      
        pframe.grid(padx=15, pady=10, sticky='w', column=0, columnspan=4)
    
        
    def new_plink(self):
        data = load_plink(gui=True)
        object_data = make_objects(data[0],data[1],data[2],data[3],data[4],\
                               data[5])
        regions = object_data[3]
        quad = regions_to_quad(regions)
        
        if data[6] == '':
            path = 'Plink data not saved'
        else:
            path = data[6]
        
        if self.show_shaded.get():
            vie = (object_data[0], object_data[1], object_data[2]) 
            # Vertices, Intersections, Edges
        else:
            vie = None
        self.p_output(regions, vie, path)
            
    def p_load_file(self):
        '''select file to load'''
        # open file options
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        filename = tkFileDialog.askopenfilename(**options)
        # TODO load(filename) - must also determine Plink vs. Knotilus
        if filename == '': # no file selected (canceled)
            return
        
        try:
            data = load_plink(filename, gui=True)
            object_data = make_objects(data[0],data[1],data[2],data[3],data[4],\
                                   data[5])
            regions = object_data[3]
        except Exception as error:
            tkMessageBox.showwarning('Loading', \
                                     'Loading failed - %s%s' \
                                     % (type(error), filename))
            print traceback.print_exc()
            return

        if self.show_shaded.get():
            vie = (object_data[0], object_data[1], object_data[2]) 
            # Vertices, Intersections, Edges       
        else:
            vie = None
        self.p_output(regions, vie, filename)
    
    def p_output(self, regions, vie, inputinfo):
        quad = regions_to_quad(regions)
        
        if self.condense.get():
            OutputWindow(self.master, quad, quad, inputinfo, condense=True)
        else:
            OutputWindow(self.master, quad, quad, inputinfo, \
                         showquad=self.show_quad.get(), \
                         showgraph=self.show_graph.get(), regions=regions)
        
        if self.show_shaded.get():
            ShadedLinkWindow(self.master, regions, vie[0], vie[1], vie[2], \
                             inputinfo) # open window to show shaded link        
        #self.master.wait_window(output.top)
        
        if self.show_link.get():
            if inputinfo != 'Plink data not saved':
                editor = plink.LinkEditor()
                editor.load(inputinfo)

class ShadedLinkWindow(object):
    '''Window to show shaded link drawing'''
    def __init__(self, master, Regions, Vertices, Intersections, Edges, \
                 inputinfo, flip=False):
        self.master = master
        self.top = Toplevel(master)
        self.top.title('Shaded link')
        Label(self.top, text=inputinfo).grid(row=0, column=0)
        Button(self.top, text='Close', command=self.top.destroy).grid(row=0, \
                                                                      column=1)
        self.height = 560
        c = Canvas(self.top, width=500, height=self.height, bg='gray')
        c.grid(columnspan=2)
        self.draw(c, Regions, Vertices, Intersections, Edges, flip)
    
    def draw(self, canvas, Regions, Vertices, Intersections, Edges, toflip):
        for region in Regions:
            if region.angle > 0:
                # draw all shaded regions (except exterior)                
                region.draw(canvas, flip=toflip, height=self.height) 
            else:
                Label(self.top, text='Background is a shaded region').grid(\
                    row=2, column=0, columnspan=2)    
        for vertex in Vertices:
            vertex.draw(canvas, flip=toflip, height=self.height)
        for inter in Intersections:
            inter.draw(canvas, flip=toflip, height=self.height)
        for edge in Edges:
            #print edge.__class__.__name__
            edge.draw(canvas, flip=toflip, height=self.height)

class SeifertBox(object):
    '''Enter Seifert data'''
    def __init__(self, master, section_font, condense, show_quad):
        self.master = master
        self.show_quad = show_quad
        self.condense = condense
        
        sframe = LabelFrame(master, text='Seifert fibered rational homology ' +\
                            'spheres', font=section_font, padx=5, pady=5)
        text = Label(sframe, text='Enter Seifert data as list\n' +\
                     '[e,(p1,q1),...,(pr,qr)]')
        text.grid(row=0, column=0)
        Button(sframe, text='Go', command=self.get_seifert).grid(row=0, \
                                                                 column=2)
                
        self.entry = Entry(sframe)
        self.entry.grid(row=0, column=1)
        
        sframe.grid(padx=15, pady=10, sticky='w', column=0, columnspan=4)
    
    def get_seifert(self):
        # will run loading and correction terms later... TODO
        stringdata = self.entry.get()
        try:
            if stringdata == '':
                raise ValueError('empty string')            
            stringdata.replace(' ','') # remove all spaces
            data = []
            
            stringdata = stringdata.split('[')[1].split(']')[0] # remove [, ]
            stringdata = stringdata.split(',(')
            data.append(int(stringdata[0])) # append e
            for pair in stringdata[1:]:
                pairlist = pair.split(',')
                pairlist[0] = int(pairlist[0])
                pairlist[1] = int(pairlist[1][:-1]) # ignore last ')'
                data.append(tuple(pairlist))
        except:
            tkMessageBox.showwarning('Failed to parse data.',
                    'Data should be [e, (p1,q1), (p2,q2), ... , (pr,qr)],' +\
                    'where e and the pi,qi are ints, pi > 1, and gcd(pi,qi) ' +\
                    '= 1. Please try again.')
            print traceback.print_exc()            
            return
        #self.data = eval(self.entry.get())
        if not correct_form(data, gui=True):
            tkMessageBox.showwarning('Invalid data form.',
                    'Data should be [e, (p1,q1), (p2,q2), ... , (pr,qr)],' +\
                    'where e and the pi,qi are ints, pi > 1, and gcd(pi,qi) ' +\
                    '= 1. Please try again.')
            print traceback.print_exc()
            return
        else:
            quad = s_quad_form(data)
            
            if self.condense.get():
                OutputWindow(self.master, quad[0], quad[0], data, \
                             condense=True)
            else:
                OutputWindow(self.master, quad[0], quad[0], data, \
                             showquad=self.show_quad.get())
            #self.master.wait_window(self.output.top)
    

class OutputWindow(object):
    '''Print output'''
    def __init__(self, master, corr_terms, quad, inputinfo, condense=False, \
                 showquad=False, showgraph=False, regions=[]):
        self.master = master
        self.top = Toplevel(master)
        self.top.title('Output')
        self.corr = corr_terms
        self.quad = quad
        self.inputinfo = inputinfo # string, eg. knotilus archive num
        self.showquad = showquad # boolean or 1,0 to print quadratic form also
        
        Button(self.top, text='Save', command=self.save).grid(row=0, column=0)
        Button(self.top, text='Copy', command=self.copy).grid(row=0, column=1)
        Button(self.top, text='Close', command=self.top.destroy).grid(row=0,\
                                                                      column=2)
        
        self.output = Text(self.top, width=62)        
        if condense: # single line output
            self.output.insert(INSERT, '%s %s' % (inputinfo, str(self.corr)))
        else:
            self.output.insert(INSERT, '%s\n\nCorrection terms:\n%s\n' \
                               % (inputinfo, str(self.corr)))
            if showquad:
                self.output.insert(INSERT, '\nQuadratic form:\n%s\n' %str(quad))
            if showgraph:
                # recomputes everything, but it's not a bottleneck so ok
                Nodes=[NodeClass(i) for i in range(len(regions))]
                t = edges_regions(Nodes,regions)
                m = maximal_subtree(t, Nodes)            
                self.output.insert(INSERT, '\nGraph Commands:\n%s\n%s\n' \
                                   % (graph_plot(t), graph_plot(m)))
        #self.output.configure(state=DISABLED) # read only
        self.output.grid(row=1, column=0, columnspan=3)
        
        scrollbar = Scrollbar(self.top)
        scrollbar.grid(row=1, column=4, sticky='n'+'s')     
        self.output.config(yscrollcommand=scrollbar.set)        
        scrollbar.config(command=self.output.yview)
        '''
        Label(self.top, text='%s'%inputinfo).grid(row=1, columnspan=3)
        Label(self.top, text='Correction terms:').grid(row=2, columnspan=3)
        Label(self.top, text=str(self.corr)).grid(row=3, columnspan=3)
        if showquad:
            Label(self.top, text='Quadratic form:').grid(row=4, columnspan=3)
            Label(self.top, text=str(quad)).grid(row=5, columnspan=3)
        # FIXME this is really ugly when it outputs
        if showgraph:
            # recomputes everything, but it's not a bottleneck so ok
            Nodes=[NodeClass(i) for i in range(len(regions))]
            t = edges_regions(Nodes,regions)
            m = maximal_subtree(t, Nodes)        
            Label(self.top, text='Graph commands:').grid(row=6, columnspan=3)
            Label(self.top, text=graph_plot(t)).grid(row=7, columnspan=3)
            Label(self.top, text=graph_plot(m)).grid(row=8, columnspan=3)
        '''
        
    def save(self):
        '''Save output to file.'''
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        options['initialfile'] = 'corr_' + self.inputinfo + '.txt'
        filename = tkFileDialog.asksaveasfilename(**options)
        
        if filename:
            corr_file = open(filename, 'w')
            corr_file.write(self.output.get(1.0, END))
            '''
            corr_file.write(self.inputinfo)
            corr_file.write('\n\nCorrection Terms:\n%s\n\n' % self.corr)
            if self.show_quad:
                corr_file.write('Quadratic Form:\n%s\n' % self.quad)
            '''
            corr_file.close()
    
    def copy(self):
        '''Copy correction terms to clipboard.'''
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(self.output.get(1.0, END))
        r.destroy()

class AboutWindow(object):
    def __init__(self, master):
        self.master = master
        self.top = Toplevel(master)
        self.top.title('About')
        
        
        about_text = \
            '''
            Hfhom 1.0
            
            Caltech SURF Summer 2013
            '''
        
        Message(self.top, text=about_text, width=1500, anchor='w').pack()
        Button(self.top, text='Close', command=self.top.destroy).pack()

if __name__ == '__main__':
    root = Tk()
    root.geometry(str(windowx) + 'x' + str(windowy))
    
    app = StartWindow(root)
    
    root.mainloop()