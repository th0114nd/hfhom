# Caltech SURF 2013
# FILE: gui.py
# 12.31.13

'''
Main user interface for entering link data.
'''

import traceback, os, sys, webbrowser
import plink
import networkx as nx
from Tkinter import *
import tkFileDialog, tkMessageBox, tkFont, ttk
import ImageTk, Image
import tkHyperlinkManager
from graph_quad import *
from knotilus_download import valid_archive_form, browser_link
from seifert import s_quad_form, correct_form, s_draw, alter_data, make_graph
from weighted_graph import GraphPopup
from gui_output import OutputWindow
from ndqf import NDQF

def regions_to_quad(regions):
    '''Return quadratic form (numpy array) given list of RegionClass objects'''
    Nodes = [NodeClass(i) for i in range(len(regions))]
    t = edges_regions(Nodes,regions)
    m = maximal_subtree(t, Nodes)
    minus = minus_maximal_subtree(t, m)
    return quad_form(t, minus, Nodes)

class StartWindow(Frame):
    def __init__(self, master):        
        self.master = master
        self.master.title('Hfhom')
        
        # make menu
        self.menubar = Menu(master)
        # File
        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label='Exit', command=self.master.destroy)
        self.menubar.add_cascade(label='File', menu=filemenu)
         
        # Options
        show_link = IntVar()
        show_shaded = IntVar()
        show_graph = IntVar()        
        show_quad = IntVar()
        show_hom = IntVar()
        self.condensed = IntVar()  
        show_weighted = IntVar()
        show_seifert = IntVar()
        optmenu = Menu(self.menubar, tearoff=0)
        optmenu.add_checkbutton(label='Print quadratic form',variable=show_quad)
        optmenu.add_checkbutton(label='Print H_1(Y) type', \
                                variable=show_hom)
        optmenu.add_checkbutton(label='Condense correction terms', \
                                variable=self.condensed, \
                                command=lambda: self.disable_quad_graph(
                                    optmenu, dbcmenu, manifoldmenu))
        dbcmenu = Menu(optmenu, tearoff=0)
        dbcmenu.add_checkbutton(label='Show original link', variable=show_link)
        dbcmenu.add_checkbutton(label='Show shaded link', variable=show_shaded)
        dbcmenu.add_checkbutton(label='Print graph commands',variable=show_graph)
        optmenu.add_cascade(label='Double branched cover', menu=dbcmenu)
        manifoldmenu = Menu(optmenu, tearoff=0)
        manifoldmenu.add_checkbutton(label='Show weighted graph', 
                                     variable=show_weighted)        
        manifoldmenu.add_checkbutton(label='Print modified Seifert data', 
                                     variable=show_seifert)
        optmenu.add_cascade(label='Plumbed 3-manifolds', menu=manifoldmenu)
        self.menubar.add_cascade(label='Options', menu=optmenu)

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
        self.path = os.path.abspath(os.path.dirname(sys.argv[0]))
        banner = True
        try: # Linux/Mac
            image = Image.open('%s/images/banner_small.png' % self.path)
        except IOError:
            try: # Windows
                image = Image.open('%s\images\banner_small.png' % self.path)
            except IOError:
                try:
                    image = Image.open(banner_small.png)
                except IOError:
                    banner = False
        if banner:
            knotimage = ImageTk.PhotoImage(image)
            bannerlabel = Label(image=knotimage)
            bannerlabel.image = knotimage # keep reference (garbage collection)
            bannerlabel.grid(row=1, sticky='w', columnspan=4)
        
        # useful stuff
        section_font = tkFont.Font(size=9) # font for headers
        note = ttk.Notebook(master)
        note.enable_traversal() # ctrl+tab cycle forward, shift+ctrl+tab back
        
        # Double branched cover of an alternating link tab
        double_cover = Frame(note)
        description1 = '\nCorrection terms for the double branched cover of ' +\
            ' an alternating link.\nInput is an alternating link.'
        Label(double_cover, text=description1, justify=LEFT).grid(row=0, \
                                            column=0, sticky='w', columnspan=4)
        knotilus = KnotilusBox(double_cover, section_font, self.condensed,
                               show_hom, show_quad, show_link, show_shaded, 
                               show_graph)
        plink = PLinkBox(double_cover, section_font, self.condensed, show_hom,
                         show_quad, show_link, show_shaded, show_graph)
        note.add(double_cover, text='Double branched cover')
        
        # Plumbed 3-manifolds tab
        plumbing = Frame(note)
        description2 = '\nCorrection terms for certain plumbed 3-manifolds.\n'+\
            'Input is Seifert data or a negative-definite weighted graph.'
        Label(plumbing, text=description2, justify=LEFT).grid(row=0, column=0,
                                                    sticky='w', columnspan=4)
        seifert = SeifertBox(plumbing, section_font, self.condensed, show_hom,
                             show_quad, show_weighted, show_seifert)
        graph = WeightedGraphBox(plumbing, section_font, self.condensed, 
                                 show_hom, show_quad, show_weighted)
        note.add(plumbing, text='Plumbed 3-manifolds')
        note.grid(sticky='w', column=0, columnspan=4, pady=5)

        # Banner image again
        if banner:
            bannerlabel2 = Label(image=knotimage)
            bannerlabel2.image = knotimage # keep reference (garbage collection)
            bannerlabel2.grid(sticky='w', columnspan=4)  
    
    def disable_quad_graph(self, menu1, menu2, menu3):
        '''
        Disable options to show quadratic form, graph commands, Seifert data.
        '''
        if self.condensed.get():
            menu1.entryconfigure('Print quadratic form', state=DISABLED)
            menu2.entryconfigure('Print graph commands', state=DISABLED)
            menu3.entryconfigure('Print modified Seifert data', state=DISABLED)
        else:
            menu1.entryconfigure('Print quadratic form', state=NORMAL)
            menu2.entryconfigure('Print graph commands', state=NORMAL)
            menu3.entryconfigure('Print modified Seifert data', state=NORMAL)
    
    def about(self):
        AboutWindow(self.master)
    
    def help(self):
        webbrowser.open('%s/README.html' % self.path)
        
class KnotilusBox(object):
    '''Knotilus archive number'''
    def __init__(self, master, section_font, condense, show_hom, show_quad,
                 show_link, show_shaded, show_graph):
        self.master = master
        self.show_quad = show_quad
        self.show_hom = show_hom
        self.show_link = show_link
        self.show_shaded = show_shaded
        self.archive_num = None
        self.show_graph = show_graph
        self.condense = condense # to show single line output
        
        kframe = LabelFrame(master, text='Knotilus archive', font=section_font,\
                            padx=5, pady=5)
        
        # new Knotilus (download from database)
        text = Label(kframe, text='Enter archive number\n(ax-b-c, eg 6x-2-1).')
        text.grid(row=0, column=0)
        self.entry = Entry(kframe, width=15)
        self.entry.grid(row=0, column=1)
        self.save_file = IntVar()
        Checkbutton(kframe, text='Save file', variable=self.save_file).grid(\
            row=0, column=2)
        Button(kframe, text='Go', command=self.knotilus).grid(row=0, column=3)
        
        # load Knotilus file
        text2 = Label(kframe, text='Open saved Knotilus file')
        text2.grid(row=1, column=0)
        Button(kframe, text='Open', command=self.k_load_file).grid(\
            row=1, column=1, sticky='w', columnspan=3)
      
        kframe.grid(padx=15, pady=5, sticky='w', column=0, columnspan=4)
            
    def knotilus(self):
        self.archive_num = self.entry.get()
        if not valid_archive_form(self.archive_num):
            tkMessageBox.showwarning('Invalid archive form.\n',\
                    'Archive number must have form ax-b-c, for ints a,b,c.')
        else:
            data = load(self.archive_num, filename=False, 
                        save=self.save_file.get(), gui=True)
            print data
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
            data = load(self.filename, filename=True)
            regions = data[3]
        except Exception as error:
            tkMessageBox.showwarning('Loading', \
                                     'Loading failed (%s)\n%s'
                                     %(self.filename, \
                                       traceback.format_exc().splitlines()[-1]))
            print traceback.print_exc()
            return
        
        if self.show_shaded.get():
            vie = (data[0], data[1], data[2]) # Vertices, Intersections, Edges
        else:
            vie = None
        self.k_output(regions, vie, self.filename)
    
    def k_output(self, regions, vie, inputinfo):
        quad = regions_to_quad(regions)
        print quad
        quadform = NDQF(quad)
        corr = quadform.correction_terms()
        struct = quadform.group.struct()
        
        if self.condense.get():
            self.output = OutputWindow(self.master, corr, struct, quad, inputinfo, \
                                       condense=True)
        else:
            self.output = OutputWindow(self.master, corr, struct, quad, inputinfo,
                                       showhom=self.show_hom.get(),
                                       showquad=self.show_quad.get(), 
                                       showgraph=self.show_graph.get(), 
                                       regions=regions)
        if self.show_shaded.get():
            ShadedLinkWindow(self.master, regions, vie[0], vie[1], vie[2],
                             inputinfo, flip=True) 
            # opens window to show shaded link
            # flips coordinates so drawn right side up (Tkinter y-axis reversed)
        
        if self.show_link.get():
            if not self.archive_num: # loaded file
                # attempt to use filename to load original link
                # e.g. '6x-1-1.txt' or '6x-1-1' will work
                # parsing on '/' will probably not work on Windows
                archive_num = self.filename.split('/')[-1].split('.txt')[0]
                if valid_archive_form(archive_num):
                    browser_link(archive_num)
                # else ignore and do nothing
            else:
                browser_link(self.archive_num) # open browser to original link

class PLinkBox(object):
    '''PLink loading'''
    def __init__(self, master, section_font, condense, show_hom, show_quad, 
                 show_link, show_shaded, show_graph):
        self.master = master
        self.show_quad = show_quad
        self.show_hom = show_hom
        self.show_link = show_link
        self.show_shaded = show_shaded     
        self.show_graph = show_graph
        self.condense = condense
        
        pframe = LabelFrame(master, text='PLink/SnapPy', font=section_font, \
                            padx=5, pady=5)
        
        # new PLink
        text = Label(pframe, text='Create a new PLink/SnapPy file.')
        text.grid(row=0, column=0)
        Button(pframe, text='Create New', command=self.new_plink).grid(row=0,
                                                                       column=1)
        
        # load PLink file
        text2 = Label(pframe, text='Load existing PLink file')
        text2.grid(row=1, column=0)
        Button(pframe, text='Open', command=self.p_load_file).grid(row=1, 
                                                        column=1, sticky='W')
      
        pframe.grid(padx=15, pady=5, sticky='w', column=0, columnspan=4)
        
    def new_plink(self):
        '''Draw new link in PLink'''
        try:
            data = load_plink(gui=True)
        except Exception as error:
            tkMessageBox.showwarning('Loading', \
                                     'Loading failed (%s)\n%s' \
                                     %(filename, \
                                       traceback.format_exc().splitlines()[-1]))
            print traceback.print_exc()
            return            
        object_data = make_objects(data[0],data[1],data[2],data[3],data[4],
                                       data[5])
        regions = object_data[3]
        if data[6] == '':
            path = 'PLink data not saved'
        else:
            path = data[6]
        
        if self.show_shaded.get():
            vie = (object_data[0], object_data[1], object_data[2]) 
            # Vertices, Intersections, Edges
        else:
            vie = None
        self.p_output(regions, vie, path)
            
    def p_load_file(self):
        '''Select PLink file to load'''
        # open file options
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        filename = tkFileDialog.askopenfilename(**options)
        if filename == '': # no file selected (canceled)
            return        
        try:
            data = load_plink(filename, gui=True)
            object_data = make_objects(data[0],data[1],data[2],data[3],data[4],
                                   data[5])
            regions = object_data[3]
        except Exception as error:
            tkMessageBox.showwarning('Loading', \
                                     'Loading failed (%s)\n%s' \
                                     %(filename,
                                       traceback.format_exc().splitlines()[-1]))
            print traceback.print_exc()
            return

        if self.show_shaded.get():
            vie = (object_data[0], object_data[1], object_data[2]) 
            # Vertices, Intersections, Edges       
        else:
            vie = None
        self.p_output(regions, vie, filename)
    
    def p_output(self, regions, vie, inputinfo):
        '''Output correction terms'''
        if regions: # non-empty (i.e. not unknot with no crossings)
            quad = regions_to_quad(regions)
            quadform = NDQF(quad)
            corr = quadform.correction_terms()
            struct = quadform.group.structure()
        else: # unknot with no crossings
            quad = 'N/A (no crossings)'
            corr = '{0}' # only 1 spin structure # TODO check this
            struct = '{1}'
    
        if self.condense.get():
            OutputWindow(self.master, corr, struct, quad, inputinfo, condense=True)
        else:
            OutputWindow(self.master, corr, struct, quad, inputinfo, \
                         showhom=self.show_hom.get(),
                         showquad=self.show_quad.get(), \
                         showgraph=self.show_graph.get(), regions=regions) 

        if self.show_shaded.get():
            ShadedLinkWindow(self.master, regions, vie[0], vie[1], vie[2],
                             inputinfo) # open window to show shaded link
        if self.show_link.get():
            if inputinfo != 'PLink data not saved': # can only do if saved
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
        Button(self.top, text='Close', command=self.top.destroy).grid(row=0,
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
    '''Seifert data'''
    def __init__(self, master, section_font, condense, show_hom, show_quad, 
                 show_weighted, show_seifert):
        self.master = master
        self.show_quad = show_quad # intvar
        self.show_hom = show_hom
        self.show_weighted = show_weighted # intvar
        self.show_seifert = show_seifert # intvar
        self.condense = condense # intvar
        self.save_file = IntVar()
        
        sframe = LabelFrame(master, text='Seifert data', font=section_font, \
                            padx=5, pady=5)
        text = Label(sframe, text='Enter Seifert data as list\n' +\
                     '[e,(p1,q1),...,(pr,qr)]')
        text.grid(row=0, column=0)
        Checkbutton(sframe, text='Save\ngraph', variable=self.save_file).grid(\
            row=0, column=2)
        Button(sframe, text='Go', command=self.get_seifert).grid(row=0, \
                                                                 column=3)
        self.entry = Entry(sframe, width=17)
        self.entry.grid(row=0, column=1)
        
        sframe.grid(padx=15, pady=10, sticky='w', column=0, columnspan=5)
    
    def get_seifert(self):
        '''Parse Seifert data, output correction terms.'''
        stringdata = self.entry.get()
        try:
            if stringdata == '':
                raise ValueError('empty string')
            # parse data            
            stringdata = stringdata.replace(' ','') # remove all spaces
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
                    '= 1.')
            print traceback.print_exc()            
            return
        #self.data = eval(self.entry.get())
        if not correct_form(data, gui=True):
            tkMessageBox.showwarning('Invalid data form.',
                    'Data should be [e, (p1,q1), (p2,q2), ... , (pr,qr)],' +\
                    'where e and the pi,qi are ints, pi > 1, and gcd(pi,qi) ' +\
                    '= 1.')
            print traceback.print_exc()
            return
        else:
            quad = s_quad_form(data)
            quadform = NDQF(quad[0])
            corr = quadform.correction_terms()
            struct = quadform.group.structure()
            if quad[1]: # reversed orientation
                pass # TODO reverse sign on correction terms
            if self.save_file.get():
                self.save(data)
            OutputWindow(self.master, corr, struct, quad[0], data,\
                             showhom=self.show_hom.get(),
                             showquad=self.show_quad.get(), 
                             condense=self.condense.get(),
                             showseifert=self.show_seifert.get(),
                             seifertdata=alter_data(data))
            if self.show_weighted.get():
                s_draw(data)
    
    def save(self, data):
        '''Save weighted star graph to file as adjacency list and node data.'''
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        filename = tkFileDialog.asksaveasfilename(**options)
        
        if filename:
            startree = make_graph(data)
            adjfile = open(filename, 'wb')
            nx.write_adjlist(startree, adjfile)            
            adjfile.write('\nDATA\n')
            adjfile.write(str(startree.nodes(data=True)))
            adjfile.close()
            print 'Graph data saved to %s' % filename

class WeightedGraphBox(object):
    '''
    Plumbed 3-manifolds given by negative-definite weighted graphs with at 
    most 2 bad vertices.
    '''
    def __init__(self, master, section_font, condense, show_hom, show_quad, 
                 show_weighted):
        self.master = master
        self.show_weighted = show_weighted # var
        self.show_quad = show_quad # var
        self.show_hom = show_hom
        self.condense = condense # var
        
        glframe = LabelFrame(master, text='Weighted graph', font=section_font,
                            padx=5, pady=5)
        glframe.grid(padx=15, pady=5, sticky='w', column=0, columnspan=4)
        
        # new graph
        text = Label(glframe, text='Create a new weighted graph,\n' +\
                     'or load an existing graph file.')
        text.grid(row=0, column=0)
        Button(glframe, text='Open editor', command=self.start_editor).grid(
            row=0, column=1)
    
    def start_editor(self):
        g = nx.Graph()
        graph = GraphPopup(self.master, g, self.condense, self.show_quad, 
                           self.show_weighted)

class AboutWindow(object):
    def __init__(self, master):
        self.master = master
        self.top = Toplevel(master)
        self.top.title('About')
        
        about_text1 = \
            '''
            Hfhom Version 1.0
            
            Hfhom was written for a Caltech SURF project in 
            summer 2013. The project is available on GitHub, at
            '''
        about_text2 = \
            '''
            
            This project is licensed under the 
            GNU General Public License;
            see LICENSE.txt for more information.
            '''
        text = Text(self.top, width=65)
        hyperlink = tkHyperlinkManager.HyperlinkManager(text)
        text.insert(INSERT, about_text1)
        text.insert(INSERT, 'https://github.com/th0114nd/hfhom', 
                    hyperlink.add(self.project_link))
        text.insert(INSERT, about_text2)
        text.configure(state=DISABLED) # read only
        text.pack()
        #Message(self.top, text=about_text, width=1500, anchor='w').pack()
        Button(self.top, text='Close', command=self.top.destroy).pack()
    
    def project_link(self):
        webbrowser.open('https://github.com/th0114nd/hfhom')

def main():
    root = Tk()
    root.geometry('440x405')
    app = StartWindow(root)
    root.mainloop()    

if __name__ == '__main__':
    main()
