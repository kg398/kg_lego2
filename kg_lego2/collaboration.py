import time
import copy
from math import pi
import numpy as np
import tkinter as tk
from functools import partial
import sys
import lego_moves as lm
import assembly as ass
import resampler as res

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
        self.quit_flag = False
        

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
        self.quit_flag = True
        self.done()
        #sys.exit()
    
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

class Menu(tk.Frame):              
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)   
        self.grid()     
        self.w = tk.Toplevel(self)
        self.w.grid()
        self.grid()
        self.mode = 0
        self.behaviour = 0
        self.modifier = 0
        self.filename = ''
        self.createWidgets()
        self.w.withdraw()
        self.w.deiconify()
        self.quit_flag = False
        

    def createWidgets(self):
        self.w.title = tk.Label(self.w,text='Robot Collaborator Configurer',font=32)
        self.w.title.grid(columnspan=3)

        #self.w.mb = tk.Menubutton(self.w,text="Menu",relief=tk.RAISED)
        #self.w.mb.grid()

        #self.w.mb.menu = tk.Menu(self.w.mb, tearoff=0)
        #self.w.mb['menu'] = self.w.mb.menu
        

        #self.w.mode_mb = tk.Menubutton(self.w.mb.menu)
        #self.w.mode_mb.grid()
        #self.w.mode_mb.mode_menu = tk.Menu(self.w.mode_mb,tearoff=0)
        #self.w.mode_mb['menu'] = self.w.mode_mb.mode_menu

        #self.w.mb.menu.add_cascade(menu=self.w.mode_mb.mode_menu,label='Mode')

        #self.w.mode_mb.mode_menu.add_checkbutton(label='1.Alternating',command=partial(self.set_mode,1),variable=self.mode_states[0])
        #self.w.mode_mb.mode_menu.add_checkbutton(label='2.Seed',command=partial(self.set_mode,2),variable=self.mode_states[1])
        #self.mode_states[self.mode].set(1)

        #self.w.behaviour_mb = tk.Menubutton(self.w.mb.menu)
        #self.w.behaviour_mb.grid()
        #self.w.behaviour_mb.behaviour_menu = tk.Menu(self.w.behaviour_mb,tearoff=0)
        #self.w.behaviour_mb['menu'] = self.w.behaviour_mb.behaviour_menu

        #self.w.mb.menu.add_cascade(menu=self.w.behaviour_mb.behaviour_menu,label='Behaviour')
        
        #self.w.behaviour_mb.behaviour_menu.add_checkbutton(label='1.mimic',command=partial(self.set_behaviour,1),variable=self.behaviour_states[0])
        #self.w.behaviour_mb.behaviour_menu.add_checkbutton(label='2.normal_dist',command=partial(self.set_behaviour,2),variable=self.behaviour_states[1])
        #self.behaviour_states[self.behaviour].set(1)


        self.mode_states = []
        self.mode_states.append(tk.IntVar())
        self.mode_states.append(tk.IntVar())

        self.w.mode_label = tk.LabelFrame(self.w, text='Mode')
        self.w.mode_label.grid()

        self.w.mode1 = tk.Checkbutton(self.w.mode_label,text='1.Alternating',command=partial(self.set_mode,0),variable=self.mode_states[0])
        self.w.mode1.grid(sticky=tk.W)
        self.w.mode2 = tk.Checkbutton(self.w.mode_label,text='2.Seed',command=partial(self.set_mode,1),variable=self.mode_states[1])
        self.w.mode2.grid(sticky=tk.W)
        self.mode_states[self.mode].set(1)


        self.behaviour_states = []
        self.behaviour_states.append(tk.IntVar())
        self.behaviour_states.append(tk.IntVar())

        self.w.behaviour_label = tk.LabelFrame(self.w, text='Behaviour')
        self.w.behaviour_label.grid(row=1,column=1)

        self.w.behaviour1 = tk.Checkbutton(self.w.behaviour_label,text='1.mimic',command=partial(self.set_behaviour,0),variable=self.behaviour_states[0])
        self.w.behaviour1.grid(sticky=tk.W)
        self.w.behaviour2 = tk.Checkbutton(self.w.behaviour_label,text='2.normal_dist',command=partial(self.set_behaviour,1),variable=self.behaviour_states[1])
        self.w.behaviour2.grid(sticky=tk.W)
        self.behaviour_states[self.behaviour].set(1)


        self.modifier_states = []
        self.modifier_states.append(tk.IntVar())
        self.modifier_states.append(tk.IntVar())
        self.modifier_states.append(tk.IntVar())

        self.w.modifier_label = tk.LabelFrame(self.w, text='Modifier')
        self.w.modifier_label.grid(row=1,column=2)

        self.w.modifier1 = tk.Checkbutton(self.w.behaviour_label,text='1.normal',command=partial(self.set_modifier,0),variable=self.modifier_states[0])
        self.w.modifier1.grid(sticky=tk.W)
        self.w.modifier2 = tk.Checkbutton(self.w.behaviour_label,text='2.fill_gaps',command=partial(self.set_modifier,1),variable=self.modifier_states[1])
        self.w.modifier2.grid(sticky=tk.W)
        self.w.modifier3 = tk.Checkbutton(self.w.behaviour_label,text='3.open_gaps',command=partial(self.set_modifier,2),variable=self.modifier_states[2])
        self.w.modifier3.grid(sticky=tk.W)
        self.modifier_states[self.modifier].set(1)

        self.w.file_label = tk.LabelFrame(self.w, text='Starting Filename')
        self.w.file_label.grid(row=1,column=3)

        self.w.filename = tk.Entry(self.w.file_label,width=16,justify=tk.LEFT)
        self.w.filename.grid()
        self.w.filename.insert(0, '.txt')



        self.w.done_button = tk.Button(self.w, text='Done', command=self.done,font=16)
        self.w.done_button.grid(row=2,column=0,columnspan=2)

        self.w.quitButton = tk.Button(self.w, text='Quit',command=self.close)
        self.w.quitButton.grid(row=2,column=2,columnspan=2) 

    def close(self):
        self.quit_flag = True
        self.done()
        #sys.exit()
    
    def done(self): 
        self.filename = self.w.filename.get()
        #self.filename+='.txt'
        self.w.withdraw()
        self.quit()
        self.destroy()

    def set_mode(self,state):
        for i in range(0,len(self.mode_states)):
            if i!=state-1:
                self.mode_states[i].set(0)
        self.mode = state

    def set_behaviour(self,state):
        for i in range(0,len(self.behaviour_states)):
            if i!=state-1:
                self.behaviour_states[i].set(0)
        self.behaviour = state

    def set_modifier(self,state):
        for i in range(0,len(self.modifier_states)):
            if i!=state-1:
                self.modifier_states[i].set(0)
        self.modifier = state

def assemble(robot):
    app = Menu()                       
    app.master.title('Collaboration Configurer')    
    app.mainloop()
    print('mode: ',app.mode)
    print('behaviour: ',app.behaviour)
    print('starting file: ',app.filename)
    if app.quit_flag == True:
        return

    model = []
    if app.filename != '':
        model = fd.import_file(app.filename)
    while True:
        human_model,nlayers,quit_flag = human_layer(model)
        if quit_flag == True:
            break
        model.append(human_model)
        model = robot_layers(robot,model,nlayers,app.behaviour)

        if app.mode == 2:
            break

    return

def human_layer(previous_layer=0):
    app = Application(previous_layer=previous_layer)                       
    app.master.title('Collaboration Human Layer')    
    app.mainloop()
    #for y in range(0,16):
    #    for x in range(0,32):
    #        print(app.layer[y][x],end='')
    #    print('')
    return app.layer, int(app.robot_layers), app.quit_flag

def robot_layers(robot,model,layers,behaviour=0,modifier=0):
    for i in range(0,layers):
        if behaviour==0:
            model = mimic(model)
        elif behaviour==1:
            model = normal_dist(model)
        
        if modifier==1:
            model = fill_gaps(model)
        elif modifier==2:
            model = open_gaps(model)
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
    """human layer is directly copied"""
    bricks = []
    bricks = fd.decode_file([model[-1]])
    for i in range(0,len(bricks)):
        bricks[i]['z']+=int(len(model))
    model.append(copy.deepcopy(fd.grid_space))
    model = fd.add_bricks(bricks,model)
    return model

def normal_dist(model):
    """robot layer is human layer copy with normal distribution disturbance"""
    return model

def weighted_normal_dist(model):
    """robot layer is human layer copy with normal distribution disturbance, with deviation weighted by previous layers, e.g. higher deviation if previous layers share same bricks"""
    return model

def reinforce(model):
    """robot layer copies pattern but attempts to overlap bricks"""
    return model

def fill_gaps(model):
    """robot layer copies pattern but dilates then erodes to fill in gaps and create bridges"""
    #first dilate then erode
    layer = res.resample_layer(model[-1])
    layer = res.dilate(model[-1])
    layer = res.erode(layer)
    layers = res.rebrick(layer)
    
    #model[-1] = copy.deepcopy(layers[choice])
    #return model
    return layers

def open_gaps(model):
    """robot layer copies pattern but erodes then dilates to separate nearby structures"""
    #first dilate then erode
    layer = res.resample_layer(model[-1])
    layer = res.erode(model[-1])
    layer = res.dilate(layer)
    layers = res.rebrick(layer)
    
    #model[-1] = copy.deepcopy(layers[choice])
    #return model
    return layers