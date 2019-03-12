import time
import copy
from math import pi
import numpy as np
import tkinter as tk
from functools import partial
import sys
import random

import lego_moves as lm
import assembly as ass
import resampler as res

import file_decoder as fd

class Application(tk.Frame):              
    def __init__(self, master=None,previous_layer=0,show_layers=True):
        tk.Frame.__init__(self, master)   
        self.show_layers=show_layers
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
        if self.show_layers==True:
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
        self.w = tk.Toplevel(self,takefocus=True)
        self.w.grid()
        self.mode = 0
        self.behaviour = 0
        self.modifier = 0
        self.filename = ''
        self.createWidgets()
        #self.w.withdraw()
        #self.w.deiconify()
        self.quit_flag = False
        self.w.config(takefocus=False)
        self.w.config(takefocus=True)

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
        self.mode_states.append(tk.IntVar())
        self.mode_states.append(tk.IntVar())
        self.mode_states.append(tk.IntVar())

        self.w.mode_label = tk.LabelFrame(self.w, text='Mode')
        self.w.mode_label.grid(sticky=tk.N)
        
        self.w.mode1 = tk.Checkbutton(self.w.mode_label,text='1.Seed: ',command=partial(self.set_mode,0),variable=self.mode_states[0])
        self.w.mode1.grid(sticky=tk.W)
        self.w.mode2 = tk.Checkbutton(self.w.mode_label,text='2.Seed: input',command=partial(self.set_mode,1),variable=self.mode_states[1])
        self.w.mode2.grid(sticky=tk.W,columnspan=3)
        self.w.mode3 = tk.Checkbutton(self.w.mode_label,text='3.Seed: random',command=partial(self.set_mode,2),variable=self.mode_states[2])
        self.w.mode3.grid(sticky=tk.W,columnspan=3)
        self.w.mode4 = tk.Checkbutton(self.w.mode_label,text='4.Alternating: regular: ',command=partial(self.set_mode,3),variable=self.mode_states[3])
        self.w.mode4.grid(sticky=tk.W,columnspan=2)
        self.w.mode5 = tk.Checkbutton(self.w.mode_label,text='5.Alternating: irregular',command=partial(self.set_mode,4),variable=self.mode_states[4])
        self.w.mode5.grid(sticky=tk.W,columnspan=3)
        self.mode_states[self.mode].set(1)

        #self.w.file_label = tk.LabelFrame(self.w, text='Starting Filename')
        #self.w.file_label.grid(row=1,column=3)

        self.w.filename = tk.Entry(self.w.mode_label,width=16,justify=tk.LEFT)
        self.w.filename.grid(row=0,column=1,columnspan=2,sticky=tk.E)
        self.w.filename.insert(0, 'example.txt')

        self.w.human_layer_spacing = tk.Entry(self.w.mode_label,width=4,justify=tk.LEFT)
        self.w.human_layer_spacing.grid(row=3,column=2,sticky=tk.E)
        self.w.human_layer_spacing.insert(0, '1')


        self.behaviour_states = []
        self.behaviour_states.append(tk.IntVar())
        self.behaviour_states.append(tk.IntVar())
        self.behaviour_states.append(tk.IntVar())
        self.behaviour_states.append(tk.IntVar())

        self.w.behaviour_label = tk.LabelFrame(self.w, text='Behaviour')
        self.w.behaviour_label.grid(row=1,column=1,sticky=tk.N)

        self.w.behaviour1 = tk.Checkbutton(self.w.behaviour_label,text='1.Mimic',command=partial(self.set_behaviour,0),variable=self.behaviour_states[0])
        self.w.behaviour1.grid(sticky=tk.W,columnspan=2)
        self.w.behaviour2 = tk.Checkbutton(self.w.behaviour_label,text='2.Random',command=partial(self.set_behaviour,1),variable=self.behaviour_states[1])
        self.w.behaviour2.grid(sticky=tk.W,columnspan=2)
        self.w.behaviour3 = tk.Checkbutton(self.w.behaviour_label,text='3.Weighted Random',command=partial(self.set_behaviour,2),variable=self.behaviour_states[2])
        self.w.behaviour3.grid(sticky=tk.W)
        self.w.behaviour4 = tk.Checkbutton(self.w.behaviour_label,text='4.Reinforce',command=partial(self.set_behaviour,3),variable=self.behaviour_states[3])
        self.w.behaviour4.grid(sticky=tk.W,columnspan=2)
        self.behaviour_states[self.behaviour].set(1)

        self.w.weight = tk.Entry(self.w.behaviour_label,width=4,justify=tk.LEFT)
        self.w.weight.grid(row=2,column=2,sticky=tk.E)
        self.w.weight.insert(0, '1')


        self.modifier_states = []
        self.modifier_states.append(tk.IntVar())
        self.modifier_states.append(tk.IntVar())
        self.modifier_states.append(tk.IntVar())
        self.modifier_states.append(tk.IntVar())
        self.modifier_states.append(tk.IntVar())

        self.w.modifier_label = tk.LabelFrame(self.w, text='Modifier')
        self.w.modifier_label.grid(row=1,column=2,sticky=tk.N)

        self.w.modifier1 = tk.Checkbutton(self.w.modifier_label,text='1.None',command=partial(self.set_modifier,0),variable=self.modifier_states[0])
        self.w.modifier1.grid(sticky=tk.W)
        self.w.modifier2 = tk.Checkbutton(self.w.modifier_label,text='2.Fill_gaps',command=partial(self.set_modifier,1),variable=self.modifier_states[1])
        self.w.modifier2.grid(sticky=tk.W)
        self.w.modifier3 = tk.Checkbutton(self.w.modifier_label,text='3.Open_gaps',command=partial(self.set_modifier,2),variable=self.modifier_states[2])
        self.w.modifier3.grid(sticky=tk.W)
        self.w.modifier4 = tk.Checkbutton(self.w.modifier_label,text='4.Semi-open gaps',command=partial(self.set_modifier,3),variable=self.modifier_states[3])
        self.w.modifier4.grid(sticky=tk.W)
        self.w.modifier5 = tk.Checkbutton(self.w.modifier_label,text='5.Random',command=partial(self.set_modifier,4),variable=self.modifier_states[4])
        self.w.modifier5.grid(sticky=tk.W)
        self.modifier_states[self.modifier].set(1)

 
        self.w.done_button = tk.Button(self.w, text='Done', command=self.done,font=16)
        self.w.done_button.grid(row=2,column=1,columnspan=1)

        self.w.quitButton = tk.Button(self.w, text='Quit',command=self.close)
        self.w.quitButton.grid(row=2,column=2,columnspan=1) 

    def close(self):
        self.quit_flag = True
        self.done()
        #sys.exit()
    
    def done(self): 
        self.filename = self.w.filename.get()
        self.human_layer_spacing = int(self.w.human_layer_spacing.get())
        self.weight = float(self.w.weight.get())
        #self.filename+='.txt'
        self.w.withdraw()
        self.quit()
        self.destroy()

    def set_mode(self,state):
        for i in range(0,len(self.mode_states)):
            if i!=state:
                self.mode_states[i].set(0)
        self.mode = state

    def set_behaviour(self,state):
        for i in range(0,len(self.behaviour_states)):
            if i!=state:
                self.behaviour_states[i].set(0)
        self.behaviour = state

    def set_modifier(self,state):
        for i in range(0,len(self.modifier_states)):
            if i!=state:
                self.modifier_states[i].set(0)
        self.modifier = state

def assemble(robot):
    app = Menu()                       
    app.master.title('Collaboration Configurer')    
    app.mainloop()
    print('mode: ',app.mode)
    print('behaviour: ',app.behaviour)
    print('modifier: ',app.modifier)
    print('starting file: ',app.filename)
    print('weight: ',app.weight)
    print('human layer spacing: ',app.human_layer_spacing)
    if app.quit_flag == True:
        return

    if app.mode==0:
        model = fd.import_file(app.filename)
        robot_layers(robot,model,100,app.behaviour,app.modifier)
    elif app.mode==1:
        human_model,nlayers,quit_flag = human_layer(layers=False)
        robot_layers(robot,[human_model],100,app.behaviour,app.modifier)
    elif app.mode==2:
        model = random_layer()
        robot_layers(robot,[model],100,app.behavior,app.modifier)
    elif app.mode==3:
        model = []
        while True:
            human_model,nlayers,quit_flag = human_layer(model,layers=False)
            if quit_flag == True:
                break
            model.append(human_model)
            model = robot_layers(robot,model,app.human_layer_spacing,app.behaviour,app.modifier)
            if model==False:
                break
    elif app.mode==4:
        model = []
        while True:
            human_model,nlayers,quit_flag = human_layer(model)
            if quit_flag == True:
                break
            model.append(human_model)
            model = robot_layers(robot,model,nlayers,app.behaviour,app,modifier)
            if model==False:
                break
    return

def human_layer(previous_layer=0,layers=True):
    app = Application(previous_layer=previous_layer,show_layers=layers)                       
    app.master.title('Collaboration Human Layer')    
    app.mainloop()
    #for y in range(0,16):
    #    for x in range(0,32):
    #        print(app.layer[y][x],end='')
    #    print('')
    return app.layer, int(app.robot_layers), app.quit_flag

def robot_layers(robot,model,layers,behaviour=0,modifier=0,weight=1):
    for i in range(0,layers):
        # resample layer into modified grid of '1's and '0's, from modifier
        if modifier==0:# mimic
            model.append(copy.deepcopy(model[-1]))
        elif modifier==1:# fill gaps
            model.append(fill_gaps(model))
        elif modifier==2:# open gaps
            model.append(open_gaps(model))
        elif modifier==3:# semi open gaps
            # not finished
            model.append(semi_open_gaps(model))
        elif modifier==4:# redistribute with normal distribution
            # not finished
            model.append(random_redist(model))

        # rebrick grid of '1's and '0's, choice from behaviour
        if behaviour==0:
            if modifier==0:
                model = mimic(model)
            else:
                model = weighted_random_choice(model,1000)
        elif behaviour==1:
            model = random_choice(model)
        elif behaviour==2:
            model = weighted_random_choice(model,weight)
        elif behaviour==3:
            model = reinforce(model)
        
        print('layer: ',i)
        for y in range(0,16):
            for x in range(0,32):
                print(model[-1][y][x],end='')
            print('')
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
        if ipt == 'n':
            return False
    return model


# functions for rebricking a layer
def mimic(model):
    """human layer is directly copied"""
    bricks = []
    bricks = fd.decode_file([model[-1]])
    for i in range(0,len(bricks)):
        bricks[i]['z']+=int(len(model))
    model.append(copy.deepcopy(fd.grid_space))
    model = fd.add_bricks(bricks,model)
    return model

def random_choice(model):
    """robot layer choice at random"""
    layer = res.resample_layer(model[-1])
    layers = res.rebrick(layer)
    index = random.randrange(0,len(layers),1)
    model[-1] = copy.deepcopy(layers[index])
    return model

def weighted_random_choice(model,weight=1):
    """robot layer choice at random, weighted by lower layer geometry"""
    layer = res.resample_layer(model[-1])
    layers = res.rebrick(layer)
    deviations = []
    max_deviation = 0
    if len(model)>1 and weight!=1:
        for i in range(0,len(layers)):
            deviations.append(res.compare_layers(model[-2],layers[i]))
            if deviations[i]>max_deviation:
                max_deviation = deviations[i]
        if weight<1:
            #weighted towards higher deviations
            for i in range(0,len(deviations)):
                deviations[i] = int(weight*max_deviation+(1-weight)*deviations[i])
        elif weight>1:
            #weighted towards lower deviations
            for i in range(0,len(deviations)):
                deviations[i] = int((1/weight)*max_deviation+(1-1/weight)*(max_deviation-deviations[i]))
        choice_array = []
        for i in range(0,len(deviations)):
            for j in range(0,deviation[i]):
                choice_array.append(i)
        index = random.choice(choice_array)
    else:
        index = random.randrange(0,len(layers),1)
    model[-1] = copy.deepcopy(layers[index])
    return model

def reinforce(model):
    """robot layer copies pattern but attempts to overlap bricks"""
    """robot layer choice at random, weighted by lower layer geometry"""
    layer = res.resample_layer(model[-1])
    layers = res.rebrick(layer)
    strength_scores = []
    max_strength = 0
    if len(model)>1:
        for i in range(0,len(layers)):
            strength_scores.append(strength_score(model[-2],layers[i]))
            if strength_scores[i]>max_strength:
                max_strength = strength_scores[i]
        choice_array = []
        for i in range(0,len(strength_scores)):
            if strength_scores[i]==max_strength:
                choice_array.append(i)
        index = random.choice(choice_array)
    else:
        index = random.randrange(0,len(layers),1)
    model[-1] = copy.deepcopy(layers[index])
    return model

def strength_score(lower_layer,upper_layer):
    """plus score for overlapping bricks, neutral for ontop of bricks, negative for overhangs, takes in rebricked upper layer (brick id starts at 2)"""
    score = 0
    bricks = fd.decode_file([upper_layer])
    for i in range(0,len(bricks)):
        corners = [[0,0],[0,0]]
        if bricks[i]['r']==0 or bricks[i]['r']==180:
            corners[0][0] = lower_layer[bricks[i]['y']][bricks[i]['x']]
            corners[0][1] = lower_layer[bricks[i]['y']][bricks[i]['x']+1]
            corners[1][0] = lower_layer[bricks[i]['y']+3][bricks[i]['x']]
            corners[1][1] = lower_layer[bricks[i]['y']+3][bricks[i]['x']+1]
        else:
            corners[0][0] = lower_layer[bricks[i]['y']][bricks[i]['x']]
            corners[0][1] = lower_layer[bricks[i]['y']][bricks[i]['x']+3]
            corners[1][0] = lower_layer[bricks[i]['y']+1][bricks[i]['x']]
            corners[1][1] = lower_layer[bricks[i]['y']+1][bricks[i]['x']+3]

        if corners[0][0]==0:
            score-=1
        if corners[0][1]==0:
            score-=1
        if corners[1][0]==0:
            score-=1
        if corners[1][1]==0:
            score-=1
        if corners[0][0]!=0 and corners[0][1]!=0 and corners[0][0]!=corners[0][1]:
            score+=1
        if corners[0][0]!=0 and corners[1][0]!=0 and corners[0][0]!=corners[1][0]:
            score+=1
        if corners[1][1]!=0 and corners[1][0]!=0 and corners[1][1]!=corners[1][0]:
            score+=1
        if corners[1][1]!=0 and corners[0][1]!=0 and corners[1][1]!=corners[0][1]:
            score+=1


    return score



# functions for modifying a layer and resampling
def fill_gaps(model):
    """robot layer copies pattern but dilates then erodes to fill in gaps and create bridges"""
    #first dilate then erode
    layer = res.resample_layer(model[-1])
    layer = res.dilate(model[-1])
    layer = res.erode(layer)
    #layers = res.rebrick(layer)
    
    #model[-1] = copy.deepcopy(layers[choice])
    return layer
    #return layers

def open_gaps(model):
    """robot layer copies pattern but erodes then dilates to separate nearby structures"""
    #first dilate then erode
    layer = res.resample_layer(model[-1])
    layer = res.erode(model[-1])
    layer = res.dilate(layer)
    #layers = res.rebrick(layer)
    
    #model[-1] = copy.deepcopy(layers[choice])
    return layer
    #return layers

def semi_open_gaps(model):
    """robot layer copies pattern but erodes then dilates to separate nearby structures but preserving more bricks"""
    layer = res.resample_layer(model[-1])

    return layer

def random_redist(model):
    """cell values are redetermined by random function proportional to surrounding brick states"""
    layer = res.resample_layer(model[-1])
    new_layer = copy.deepcopy(layer)
    kernel = [[0,1,2,1,0],
              [1,6,8,6,1],
              [2,8,10,8,2],
              [1,6,8,6,1],
              [0,1,2,1,0]]
    for y in range(2,14):
        for x in range(2,30):
            choice_array = []
            for i in range(0,5):
                for j in range(0,5):
                    for k in range(0,kernel[i][j]):
                        choice_array.append(layer[y+i-2][x+j-2])
            new_layer[y][x] = random.choice(choice_array)
    return new_layer