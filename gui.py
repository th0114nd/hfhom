# Caltech SURF 2013
# FILE: gui3.py
# 08.02.13

'''
Main user interface for entering link data.
less popup windows than gui.py
'''

# main/start window dimensions
windowx = 450
windowy = 450

import traceback
from Tkinter import *
import tkFileDialog, tkMessageBox, ImageTk, Image, tkFont
from graph_quad import *
from knotilus_download import valid_archive_form
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
        viewmenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='View', menu=viewmenu)

        # Help
        helpmenu = Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label='Instructions', command=self.help)
        helpmenu.add_command(label='About', command=self.about)
        self.menubar.add_cascade(label='Help', menu=helpmenu)
        
        master.config(menu=self.menubar)
        
        # Title
        Label(master, text='Heegaard Floer Correction Terms', \
              font=tkFont.Font(weight='bold')).pack(anchor='w')        
        
        # Banner image
        image = Image.open('banner_small.png')
        knotimage = ImageTk.PhotoImage(image)
        
        bannerlabel = Label(image=knotimage)
        bannerlabel.image = knotimage # keep a reference! (else garbage collected)
        bannerlabel.pack(anchor='w')            
        
        # Subtitle
        Label(master, text='Actually just quadratic form...').pack(anchor='w')
        
        # useful stuff
        knotilus = KnotilusBox(master)
        plink = PlinkBox(master)
        seifert = SeifertBox(master)
        
        # Banner image again        
        bannerlabel2 = Label(image=knotimage)
        bannerlabel2.image = knotimage # keep a reference! (else garbage collected)
        bannerlabel2.pack(expand=1,anchor='w')  
        
        #canvas = Canvas(frame, bg="black", width=500, height=500)
        #canvas.pack()        
        #canvas.create_image(150, 150, image=knotimage)
        #canvas.pack()
            
        #frame.pack()
        
    def loadfile(self):
        '''select file to load'''
        # open file options
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        filename = tkFileDialog.askopenfilename(**options)
        # TODO load(filename) - must also determine Plink vs. Knotilus
        if filename:
            plinkknotilus = LoadPopup(self.master)
            self.master.wait_window(plinkknotilus.top)
        else: # no file selected (canceled)
            return
        
        try:
            if plinkknotilus.plink:
                data = load_plink(filename,gui=True)
                regions = make_objects(data[0],data[1],data[2],data[3],data[4],\
                                       data[5])[3]
            elif not plinkknotilus.plink: # knotilus
                regions = load(filename, True, False)[3]
            else: # canceled
                return
        except Exception as error:
            tkMessageBox.showwarning('Loading', \
                                     'Loading failed - %s%s'%(type(error),filename))
            print traceback.print_exc()
            return
        
        quad = self.regions_to_quad(regions)
        OutputWindow(self.master, quad, filename)
    
    def new_plink(self):
        # problem with load_plink: editor.window.mainloop() - won't proceed
        # until Hfhom window is closed...
        pass
        

        
    def seifert(self):
        self.p = Seifert_popup(self.master)
        self.master.wait_window(self.p.top)
        
        quad = s_quad_form(self.p.data)
        
        self.output = OutputWindow(self.master, quad[0], self.p.data)
        self.master.wait_window(self.output.top)
     
      
    
    def dehn(self):
        print 'dehn'
    
    def show_original(self):
        pass
    
    def show_shaded(self):
        pass
    
    def about(self):
        print 'about'
    
    def help(self):
        print 'help'    


class KnotilusBox(object):
    '''Enter Knotilus archive number'''
    def __init__(self, master):
        self.master = master
        
        kframe = LabelFrame(master, text='Knotilus', padx=5, pady=5)
        
        # new Knotilus (download from database)
        text = Label(kframe, text='Enter archive number (ax-b-c).')
        text.grid(row=0, column=0)
        Button(kframe, text='Go', command=self.knotilus).grid(row=0, column=2)
                
        self.entry = Entry(kframe)
        self.entry.grid(row=0, column=1)
        
        # load Knotilus file
        text2 = Label(kframe, text='Open saved Knotilus file')
        text2.grid(row=1, column=0)
        Button(kframe, text='Open', command=self.k_load_file).grid(row=1, column=1, sticky='W')
      
        kframe.pack(padx=15, pady=10, anchor='w')
            
    def knotilus(self):
        # will run loading and correction terms later... TODO
        self.archive_num = self.entry.get()
        if not valid_archive_form(self.archive_num):
            tkMessageBox.showwarning('Invalid archive form.\n',\
                    'Archive number must have form ax-b-c, for ints a,b,c. ' +\
                    'Please try again.')
        else:
            regions = load(self.archive_num, False, False, gui=True)[3]      
    
            quad = regions_to_quad(regions)
            
            # TODO: ouptut correction terms not quad
            self.output = OutputWindow(self.master, quad, self.archive_num)
            #self.master.wait_window(self.output.top)
            
            # TODO: clear input in entry box
    
    def k_load_file(self):
        '''select file to load'''
        # open file options
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        filename = tkFileDialog.askopenfilename(**options)

        if filename == '': # canceled
            return
        
        try:
            regions = load(filename, True, False)[3]
        except Exception as error:
            tkMessageBox.showwarning('Loading', \
                                     'Loading failed - %s%s'%(type(error),filename))
            print traceback.print_exc()
            return
        
        quad = regions_to_quad(regions)
        
        self.output = OutputWindow(self.master, quad, filename)
        #self.master.wait_window(self.output.top)

class PlinkBox(object):
    '''Plink loading'''
    def __init__(self, master):
        self.master = master
        
        pframe = LabelFrame(master, text='Plink/SnapPy', padx=5, pady=5)
        
        # new Plink???
        text = Label(pframe, text='Create a new Plink/SnapPy file.')
        text.grid(row=0, column=0)
        Button(pframe, text='Create New', command=self.new_plink).grid(row=0, column=1)
        
        # load Plink file
        text2 = Label(pframe, text='Load existing Plink file')
        text2.grid(row=1, column=0)
        Button(pframe, text='Open', command=self.p_load_file).grid(row=1, column=1, sticky='W')
      
        pframe.pack(padx=15, pady=10, anchor='w')
    
    def new_plink(self):
        pass
        
    def plink(self):
        data = load_plink(filename,gui=True)
        regions = make_objects(data[0],data[1],data[2],data[3],data[4],\
                                               data[5])[3]
        quad = regions_to_quad(regions)
        
        # TODO: ouptut correction terms not quad
        OutputWindow(self.master, quad, self.archive_num)
        #self.master.wait_window(self.output.top)
            
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
            data = load_plink(filename,gui=True)
            regions = make_objects(data[0],data[1],data[2],data[3],data[4],\
                                   data[5])[3]            
        except Exception as error:
            tkMessageBox.showwarning('Loading', \
                                     'Loading failed - %s%s'%(type(error),filename))
            print traceback.print_exc()
            return
        
        quad = regions_to_quad(regions)
        OutputWindow(self.master, quad, filename)
        #self.master.wait_window(output.top)        

class SeifertBox(object):
    '''Enter Seifert data'''
    def __init__(self, master):
        self.master = master
        
        sframe = LabelFrame(master, text='Seifert', padx=5, pady=5)
        text = Label(sframe, text='Enter Seifert data as list\n' +\
                     '[e,(p1,q1),...,(pr,qr)]')
        text.grid(row=0, column=0)
        Button(sframe, text='Go', command=self.get_seifert).grid(row=0, column=2)
                
        self.entry = Entry(sframe)
        self.entry.grid(row=0, column=1)
        
        sframe.pack(padx=15, pady=10, anchor='w')
    
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
                    'where e and the pi,qi are ints, pi > 1, and gcd(pi,qi) = 1. ' +\
                    'Please try again, or close the Seifert input window.')
            print traceback.print_exc()            
            return
        #self.data = eval(self.entry.get()) # TODO: put in help file - eval lets you evaluate stuff...
        if not correct_form(data, gui=True):
            tkMessageBox.showwarning('Invalid data form.',
                    'Data should be [e, (p1,q1), (p2,q2), ... , (pr,qr)],' +\
                    'where e and the pi,qi are ints, pi > 1, and gcd(pi,qi) = 1. ' +\
                    'Please try again, or close the Seifert input window.')
            print traceback.print_exc()
            return
        else:
            quad = s_quad_form(data)
        
            OutputWindow(self.master, quad[0], data)
            #self.master.wait_window(self.output.top)
    

        
class OutputWindow(object):
    '''Print output'''
    def __init__(self, master, corr_terms, inputinfo):
        self.master = master
        self.top = Toplevel(master)
        self.top.title('Output')
        self.corr = corr_terms
        self.inputinfo = inputinfo # string, eg. knotilus archive num
        
        Button(self.top, text='Save', command=self.save).grid(row=0,column=0)
        Button(self.top, text='Copy', command=self.copy).grid(row=0,column=1)
        Button(self.top, text='Close', command=self.top.destroy).grid(row=0,column=2)
        
        Label(self.top, text='%s'%inputinfo).grid(row=1, columnspan=3)
        Label(self.top, text='Quadratic form:').grid(row=2, columnspan=3) #TODO: corr terms
        Label(self.top, text=str(self.corr)).grid(row=3, columnspan=3)
        
    def save(self):
        pass
    
    def copy(self):
        # copy to clipboard
        pass
        

if __name__ == '__main__':
    root = Tk()
    root.geometry(str(windowx) + 'x' + str(windowy))
    
    app = StartWindow(root)
    
    root.mainloop()