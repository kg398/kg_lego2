import time
import copy
from math import pi
import numpy as np
import tkinter as tk
from functools import partial

import file_decoder as fd

class Application(tk.Frame):              
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)   
        self.w = tk.Toplevel(self)
        self.grid()
        self.w.grid()                       
        self.createWidgets()

    def createWidgets(self):
        self.quitButton = tk.Button(self, text='Quit',
            command=self.quit,activeforeground='#0f0',activebackground='#00f')
        #self.quitButton.grid() 

        self.w.quitButton = tk.Button(self.w, text='Quit',
            command=self.done,activeforeground='#0f0',activebackground='#00f')
        self.w.quitButton.grid()          

    def done(self): 
        self.quit()
        self.destroy()


def test():
    app = Application()                       
    app.master.title('Sample application')    
    app.mainloop()

