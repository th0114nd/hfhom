# Caltech SURF 2013
# FILE: gui.py
# 07.16.13

'''
Main user interface for entering link data.
'''

# main/start window dimensions
windowx = 400
windowy = 100

import traceback
from Tkinter import *
import tkFileDialog, tkMessageBox, ImageTk
from graph_quad import *
from knotilus_download import valid_archive_form
from seifert import s_quad_form, correct_form

class StartWindow(Frame):
    def __init__(self, master):
        self.master = master
        
        self.master.title('Hfhom')
        
        frame = Frame(master, width=windowx, height=windowy, bg='gray')
        #frame.pack()
        
        # http://effbot.org/tkinterbook/menu.htm
        # make menu
        self.menubar = Menu(root)
        # File
        filemenu = Menu(self.menubar, tearoff=0)
        
        # File > New options
        submenu = Menu(filemenu, tearoff=0)
        submenu.add_command(label='Plink', command=self.new_plink)
        submenu.add_command(label='Knotilus', command=self.new_knotilus)
        submenu.add_command(label='Seifert data', command=self.seifert)
        submenu.add_command(label='Dehn surgery', command=self.dehn)
        filemenu.add_cascade(label='New', menu=submenu)
        
        filemenu.add_command(label='Open file...', command=self.loadfile)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=root.quit)
        self.menubar.add_cascade(label='File', menu=filemenu)
    
        # View
        viewmenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='View', menu=viewmenu)
        viewmenu.add_command(label='Show original link', \
                             command=self.show_original)
        viewmenu.add_command(label='Show shaded link', command=self.show_shaded)
        
        # Help
        helpmenu = Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label='Instructions', command=self.help)
        helpmenu.add_command(label='About', command=self.about)
        self.menubar.add_cascade(label='Help', menu=helpmenu)
        
        master.config(menu=self.menubar)
        
        Label(master, text='Correction terms: ').pack()
        Label(master, text='Actually just quadratic form...').pack()
        
        knotimage = ImageTk.PhotoImage(file='23x-1-1.png')
        canvas = Canvas(frame, bg="black", width=500, height=500)
        #canvas.pack()        
        canvas.create_image(150, 150, image=knotimage)
        canvas.pack()
            
        #frame.pack()
        
    def loadfile(self):
        '''select file to load'''
        # open file options
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        filename = tkFileDialog.askopenfilename(**options)
        # TODO load(filename) - must also determine Plink vs. Knotilus
        plinkknotilus = LoadPopup(self.master)
        self.master.wait_window(plinkknotilus.top)
        
        try:
            if plinkknotilus.plink == True:
                data = load_plink(filename)
                regions = make_objects(data[0],data[1],data[2],data[3],data[4],\
                                       data[5])[3]
            elif plinkknotilus.plink == False: # knotilus
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
        
    def new_knotilus(self):
        self.k = Knotilus_popup(self.master)
        self.master.wait_window(self.k.top)
        
        regions = load(self.k.archive_num, False, False)[3]      

        quad = self.regions_to_quad(regions)
        
        # TODO: ouptut correction terms not quad
        self.output = OutputWindow(self.master, quad, self.k.archive_num)
        self.master.wait_window(self.output.top)
        
    def seifert(self):
        self.p = Seifert_popup(self.master)
        self.master.wait_window(self.p.top)
        
        quad = s_quad_form(self.p.data)
        
        self.output = OutputWindow(self.master, quad[0], self.p.data)
        self.master.wait_window(self.output.top)
     
    def regions_to_quad(self, regions):
        '''input list of regions, output numpy array for quadratic form'''
        Nodes = [NodeClass(i) for i in range(len(regions))]
        t = edges_regions(Nodes,regions)
        m = maximal_subtree(t, Nodes)
        minus = minus_maximal_subtree(t, m)
        return quad_form(t, minus, Nodes)         
    
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

class LoadPopup(object):
    '''choose Plink vs Knotilus loading'''
    def __init__(self, master):
        self.top = Toplevel(master)
        self.plink = None
        Label(self.top, text='Parse selected file as...').pack()
        Button(self.top, text='Plink', command=self.loadplink).pack(side=LEFT)
        Button(self.top, text='Cancel', command=self.exit).pack(side=RIGHT)
        Button(self.top, text='Knotilus', command=self.loadknotilus).pack(side=RIGHT)
    
    def loadplink(self):
        self.plink = True
        self.exit()

    def loadknotilus(self):
        self.plink = False
        self.exit()
    
    def exit(self):
        self.top.destroy()

class Knotilus_popup(object):
    '''Enter Knotilus archive number'''
    def __init__(self, master):
        self.master = master
        self.top = Toplevel(master)
        self.top.title('Knotilus Archive')
        
        self.archive_num = 'hi'
        
        text = Label(self.top, text='Enter archive number (ax-b-c).\n' +\
                     'Press <Enter> when finished.')
        text.pack(side = LEFT)
        
        self.entry = Entry(self.top)
        self.entry.pack(side = RIGHT)

        self.entry.bind('<Return>', self.get_archive)
    
    def get_archive(self, event):
        # will run loading and correction terms later... TODO
        self.archive_num = self.entry.get()
        if not valid_archive_form(self.archive_num):
            tkMessageBox.showwarning('Invalid archive form.\n',\
                    'Archive number must have form ax-b-c, for ints a,b,c. ' +\
                    'Please try again, or close the Knotilus Archive input window.')
        else:
            self.exit()
    
    def exit(self):
        self.top.destroy()

class Seifert_popup(object):
    '''Enter Seifert data'''
    def __init__(self, master):
        self.master = master
        self.top = Toplevel(master)
        self.top.title('Seifert')
        
        self.data = []
        
        text = Label(self.top, text='Enter Seifert data.\n' +\
                     'Press <Enter> when finished.')
        text.pack(side = LEFT)
        
        self.entry = Entry(self.top)
        self.entry.pack(side = RIGHT)

        self.entry.bind('<Return>', self.get_seifert)
    
    def get_seifert(self, event):
        # will run loading and correction terms later... TODO
        self.data = eval(self.entry.get()) # TODO: put in help file - eval lets you evaluate stuff...
        if not correct_form(self.data):
            tkMessageBox.showwarning('Invalid data form.',
                    'Data should be [e, (p1,q1), (p2,q2), ... , (pr,qr)],' +\
                    'where e and the pi,qi are ints, pi > 1, and gcd(pi,qi) = 1.' +\
                    'Please try again, or close the Seifert input window.')
        else:
            self.exit()
    
    def exit(self):
        self.top.destroy()
        
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