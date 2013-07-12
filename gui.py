# Panavia Shou

'''
Main user interface for entering link data.
'''

from Tkinter import *
from classes import *

def plink():
    print 'plink'

def plink_load():
    print 'plink_load'

def knotilus():
    print 'knotilus'

if __name__ == '__main__':
    root = Tk()
    root.geometry('500x560')
    
    c = Canvas(root, width=500, height=560, bg='gray')
    
    # Make buttons!
    plink_button = Button(root, text='Draw link', command=plink)
    plink_load_button = Button(root, text='Load link', command=plink_load)
    knotilus_button = Button(root, text='Knotilus???', command=knotilus)
    quit_button = Button(root, text='Quit', command=quit)
    
    plink_button.grid(row=0, column=0)
    plink_load_button.grid(row=0, column=1)
    knotilus_button.grid(row=0, column=2)
    quit_button.grid(row=0, column=3)
    c.grid(columnspan=4)

    root.mainloop()