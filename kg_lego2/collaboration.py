import time
import copy
from math import pi
import numpy as np
import tkinter as tk
from functools import partial
import sys
import lego_moves as lm
import assembly as ass

import file_decoder as fd

class Application(tk.Frame):              
    def __init__(self, master=None,previous_layer=0):
        tk.Frame.__init__(self, master)   
        self.grid()     
        self.w = tk.Toplevel(self)
        self.w.grid()
        self.grid()
        if previous_layer == 0 or previous_layer == []:
            self.previous_layer = copy.deepcopy(fd.grid_space)
        else:
            self.previous_layer=previous_layer[-1]
        self.createWidgets()
        self.new_layer()
        self.brick_coords = [None,None]
        self.bricks = 0
        self.w.withdraw()
        self.w.deiconify()
        

    def createWidgets(self):        
        self.w.lego_grid = tk.Frame(self.w,  borderwidth='1m',height=16,width=32)
        for x in range(0,32):
            self.w.lego_grid.columnconfigure(x,minsize='7m')
        for x in range(0,16):
            self.w.lego_grid.rowconfigure(x,minsize='7m')
        #self.lego_grid.grid_propagate(0)
        self.w.lego_grid.grid(row=0,column=0)

        self.w.lego_buttons = copy.deepcopy(fd.grid_space)
        for i in range(0,16):
            for j in range(0,32):
                if self.previous_layer[i][j] == 0:
                    self.w.lego_buttons[i][j] = tk.Button(self.w.lego_grid, text='0', command=partial(self.save_brick,i,j),width=2,background='#fff')
                else:
                    self.w.lego_buttons[i][j] = tk.Button(self.w.lego_grid, text='0', command=partial(self.save_brick,i,j),width=2,background='#5f5')
                self.w.lego_buttons[i][j].grid(column=j,row=i)

        self.w.robot_layer_label = tk.LabelFrame(self.w.lego_grid, text='No. robot layers')
        self.w.robot_layer_label.grid(row=16,columnspan=5,sticky=tk.W)

        self.w.robot_layer_demand = tk.Entry(self.w.robot_layer_label,width=16,justify=tk.RIGHT)
        self.w.robot_layer_demand.grid()
        self.w.robot_layer_demand.insert(0, '1')

        self.w.done_button = tk.Button(self.w.lego_grid, text='Done', command=self.done,font=16)
        self.w.done_button.grid(row=16,column=15,columnspan=2)

        self.w.quitButton = tk.Button(self.w.lego_grid, text='Quit',command=self.close)
        self.w.quitButton.grid(row=16,column=30,columnspan=2) 

    def close(self):
        self.done()
        sys.exit()
    
    def done(self): 
        self.robot_layers = self.w.robot_layer_demand.get()
        self.w.withdraw()
        self.quit()
        self.destroy()

    def new_layer(self):
        self.layer = copy.deepcopy(fd.grid_space)

    def save_brick(self,i=0,j=0):
        if self.brick_coords == [None,None]:
            self.brick_coords = [i,j]
            for y in range(0,16):
                for x in range(0,32):
                    self.w.lego_buttons[y][x].config(state=tk.DISABLED)

            if i>0:
                if j>2:
                    self.w.lego_buttons[i-1][j-3].config(state=tk.NORMAL)
                if j<29:
                    self.w.lego_buttons[i-1][j+3].config(state=tk.NORMAL)
            if i>2:
                if j>0:
                    self.w.lego_buttons[i-3][j-1].config(state=tk.NORMAL)
                if j<31:
                    self.w.lego_buttons[i-3][j+1].config(state=tk.NORMAL)
            if i<15:
                if j>2:
                    self.w.lego_buttons[i+1][j-3].config(state=tk.NORMAL)
                if j<29:
                    self.w.lego_buttons[i+1][j+3].config(state=tk.NORMAL)
            if i<13:
                if j>0:
                    self.w.lego_buttons[i+3][j-1].config(state=tk.NORMAL)
                if j<31:
                    self.w.lego_buttons[i+3][j+1].config(state=tk.NORMAL)
        else:
            yrange = range(i,self.brick_coords[0]+1,1)
            xrange = range(j,self.brick_coords[1]+1,1)
            if i>self.brick_coords[0]:
                yrange = range(i,self.brick_coords[0]-1,-1)
            if j>self.brick_coords[1]:
                xrange = range(j,self.brick_coords[1]-1,-1)

            if self.layer[self.brick_coords[0]][self.brick_coords[1]] == 0:
                self.bricks += 1
                for y in yrange:
                    for x in xrange:
                        self.layer[y][x] = self.bricks
                        self.w.lego_buttons[y][x].config(text=self.bricks,background='#8cf')
            else:
                for y in yrange:
                    for x in xrange:
                        self.layer[y][x] = 0
                        if self.previous_layer[y][x] == 0:
                            self.w.lego_buttons[y][x].config(text='0',background='#fff')
                        else:
                            self.w.lego_buttons[y][x].config(text='0',background='#5f5')

            for y in range(0,16):
                for x in range(0,32):
                    self.w.lego_buttons[y][x].config(state=tk.NORMAL)
            self.brick_coords = [None,None]




def human_layer(previous_layer=0):
    app = Application(previous_layer=previous_layer)                       
    app.master.title('Sample application')    
    app.mainloop()

    #for y in range(0,16):
    #    for x in range(0,32):
    #        print(app.layer[y][x],end='')
    #    print('')

    return app.layer, int(app.robot_layers)

def assemble(robot,model,layers):
    for i in range(0,layers):
        model = mimic(model)
        #print('layer: ',i)
        #for y in range(0,16):
        #    for x in range(0,32):
        #        print(model[-1][y][x],end='')
        #    print('')
        bricks = fd.decode_file([model[-1]])
        for j in range(0,len(bricks)):
            bricks[j]['z']+=len(model)-1
        que,opt = ass.sort_bricks_ass(bricks,copy.deepcopy(model))
        print(opt)
        print(len(que))
        print("x\ty\tz\tp\tr\tex\tey")
        for i in range(0,len(que)):
            print(que[i]['x'],'\t',que[i]['y'],'\t',que[i]['z'],'\t',que[i]['p'],'\t',que[i]['r'],'\t',que[i]['ye'],'\t',que[i]['xe'])
        ipt = input('Continue(y/n)?')
        if ipt == 'y':
            lm.assemble(robot,que)
    return model

def mimic(model):
    bricks = []
    bricks = fd.decode_file([model[-1]])
    for i in range(0,len(bricks)):
        bricks[i]['z']+=int(len(model))
    model.append(copy.deepcopy(fd.grid_space))
    model = fd.add_bricks(bricks,model)
    return model