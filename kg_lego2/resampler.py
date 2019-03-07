# Functions for reading lego structure file, decoding and sorting
import time
import random
import copy
import math
import numpy as np
import itertools

import file_decoder as fd

def resample_layer(layer):
    """resample layer into all '1's"""
    for y in range(0,16):
        for x in range(0,32):
            if layer[y][x] != 0:
                layer[y][x] = 1
    return layer


def resample_func_example(layer):
    """some transformation on sea of '1's"""
    #do something to the layer
    return layer

# copy for each direction (+x -y, etc...)

def rebrick(layer):
    """find most accurate brick representations of so1's"""
    # find all representations
    layers = recursive_populate_layer_xy(layer)
    # copy for other directions
    layers_nxy = recursive_populate_layer_nxy(layer)
    for i in range(0,len(layers_nxy)):
        layer_match_flag = 0
        for j in range(0,len(layers)):
            if layers_match(layers[j],layers_nxy[i]):
                layer_match_flag = 1
        if layer_match_flag == 0:
            layers.append(layers_nxy[i])

    layers_xny = recursive_populate_layer_xny(layer)
    for i in range(0,len(layers_xny)):
        layer_match_flag = 0
        for j in range(0,len(layers)):
            if layers_match(layers[j],layers_xny[i]):
                layer_match_flag = 1
        if layer_match_flag == 0:
            layers.append(layers_xny[i])

    layers_nxny = recursive_populate_layer_nxny(layer)
    for i in range(0,len(layers_nxny)):
        layer_match_flag = 0
        for j in range(0,len(layers)):
            if layers_match(layers[j],layers_nxny[i]):
                layer_match_flag = 1
        if layer_match_flag == 0:
            layers.append(layers_nxny[i])

    # remove any remaining '1's in each layer
    for i in range(0,len(layers)):
        for y in range(0,16):
            for x in range(0,32):
                if layers[i][y][x]==1:
                    layers[i][y][x] = 0

    #print('prerejected layers')
    #for i in range(0,len(layers)):
    #    print('\nlayer: ',i)
    #    for y in range(0,16):
    #        for x in range(0,32):
    #            print(layers[i][y][x],end='')
    #        print('')

    # decimate all poor representations
    min_deviation = 32*16
    deviation = []
    for i in range(0,len(layers)):
        deviation.append(compare_layers(layer,layers[i]))
        if deviation[i] < min_deviation:
            min_deviation = deviation[i]
        print(i,' deviation: ',deviation[i])
    final_layers = []
    for i in range(0,len(layers)):
        if deviation[i]==min_deviation:
            final_layers.append(layers[i])

    # for each brick in each final layer, check if removing brick affects deviation, if not copy layer
    # repeat until all layers are worsened in this process
    n = 0
    while True:
        print(n)
        n+=1
        change_flag = 0
        #for each layer
        for i in range(0,len(final_layers)):
            nbricks = 0
            #get deviation
            deviation = compare_layers(layer,final_layers[i])
            #get number of bricks
            for y in range(0,16):
                for x in range(0,32):
                    if final_layers[i][y][x] > nbricks:
                        nbricks = final_layers[i][y][x]
            #for each brick:
            for j in range(2,nbricks+1):
                #copy layer
                new_layer = copy.deepcopy(final_layers[i])
                #remove that brick
                for y in range(0,16):
                    for x in range(0,32):
                        if new_layer[y][x] == j:
                            new_layer[y][x] = 0
                #check if new layer is unique
                old_flag = 0
                for k in range(0,len(final_layers)):
                    if layers_match(new_layer,final_layers[k]):
                        old_flag = 1
                #if unique
                if old_flag == 0:
                    #compare deviation
                    new_deviation = compare_layers(layer,new_layer)
                    if new_deviation<deviation:
                        #replace layer is better
                        final_layers[i] = copy.deepcopy(new_layer)
                        change_flag = 1
                    elif new_deviation == deviation:
                        #append layer if the same
                        final_layers.append(copy.deepcopy(new_layer))
                        change_flag = 1
        if change_flag == 0:
            break

    # re decimate
    min_deviation = 32*16
    deviation = []
    for i in range(0,len(final_layers)):
        deviation.append(compare_layers(layer,final_layers[i]))
        if deviation[i] < min_deviation:
            min_deviation = deviation[i]
        print(i,' deviation: ',deviation[i])

    final_final_layers = []
    for i in range(0,len(final_layers)):
        if deviation[i]==min_deviation:
            final_final_layers.append(final_layers[i])

    # for each brick in each layer, check if it can be moved and if moving changes the deviation, if not copy layer
    # repeat until all layers are worsened in this process
    n = 0
    while True:
        print(n)
        n+=1
        change_flag = 0
        #for each layer
        for i in range(0,len(final_final_layers)):
            nbricks = 0
            #get deviation
            deviation = compare_layers(layer,final_final_layers[i])
            #get number of bricks
            for y in range(0,16):
                for x in range(0,32):
                    if final_final_layers[i][y][x] > nbricks:
                        nbricks = final_final_layers[i][y][x]
            #for each brick
            for j in range(2,nbricks+1):
                #find brick direction and origin
                dir = 0
                xy = [0,0]
                break_flag = 0
                for y in range(0,16):
                    if break_flag == 1:
                        break
                    for x in range(0,32):
                        if final_final_layers[i][y][x] == j:
                            xy[0]=x
                            xy[1]=y
                            break_flag = 1
                            break
                n = 0
                while True:
                    if final_final_layers[i][xy[1]][xy[0]+n] != j:
                        if n>3:
                            dir = 90
                        break
                    n+=1
                for n in range(0,4):
                    #create a copy
                    new_layer = copy.deepcopy(final_final_layers[i])
                    #move bricks by 1 space
                    space_flag = 0
                    if n == 0:
                        if dir == 0:
                            if xy[0]+2<32:
                                if new_layer[xy[1]][xy[0]+2] == 0 and new_layer[xy[1]+1][xy[0]+2] == 0 and new_layer[xy[1]+2][xy[0]+2] == 0 and new_layer[xy[1]+3][xy[0]+2] == 0:
                                    new_layer[xy[1]][xy[0]+2] = j
                                    new_layer[xy[1]+1][xy[0]+2] = j
                                    new_layer[xy[1]+2][xy[0]+2] = j
                                    new_layer[xy[1]+3][xy[0]+2] = j
                                    new_layer[xy[1]][xy[0]] = 0
                                    new_layer[xy[1]+1][xy[0]] = 0
                                    new_layer[xy[1]+2][xy[0]] = 0
                                    new_layer[xy[1]+3][xy[0]] = 0
                                    space_flag = 1
                        elif dir == 90:
                            if xy[0]+4<32:
                                if new_layer[xy[1]][xy[0]+4] == 0 and new_layer[xy[1]+1][xy[0]+4] == 0:
                                    new_layer[xy[1]][xy[0]+4] = j
                                    new_layer[xy[1]+1][xy[0]+4] = j
                                    new_layer[xy[1]][xy[0]] = 0
                                    new_layer[xy[1]+1][xy[0]] = 0
                                    space_flag = 1
                    elif n == 1:
                        if dir == 90:
                            if xy[1]+2<16:
                                if new_layer[xy[1]+2][xy[0]] == 0 and new_layer[xy[1]+2][xy[0]+1] == 0 and new_layer[xy[1]+2][xy[0]+2] == 0 and new_layer[xy[1]+2][xy[0]+3] == 0:
                                    new_layer[xy[1]+2][xy[0]] = j
                                    new_layer[xy[1]+2][xy[0]+1] = j
                                    new_layer[xy[1]+2][xy[0]+2] = j
                                    new_layer[xy[1]+2][xy[0]+3] = j
                                    new_layer[xy[1]][xy[0]] = 0
                                    new_layer[xy[1]][xy[0]+1] = 0
                                    new_layer[xy[1]][xy[0]+2] = 0
                                    new_layer[xy[1]][xy[0]+3] = 0
                                    space_flag = 1
                        elif dir == 0:
                            if xy[1]+4<16:
                                if new_layer[xy[1]+4][xy[0]] == 0 and new_layer[xy[1]+4][xy[0]+1] == 0:
                                    new_layer[xy[1]+4][xy[0]] = j
                                    new_layer[xy[1]+4][xy[0]+1] = j
                                    new_layer[xy[1]][xy[0]] = 0
                                    new_layer[xy[1]][xy[0]+1] = 0
                                    space_flag = 1
                    elif n == 2:
                        if dir == 0:
                            if xy[0]-1>-1:
                                if new_layer[xy[1]][xy[0]-1] == 0 and new_layer[xy[1]+1][xy[0]-1] == 0 and new_layer[xy[1]+2][xy[0]-1] == 0 and new_layer[xy[1]+3][xy[0]-1] == 0:
                                    new_layer[xy[1]][xy[0]-1] = j
                                    new_layer[xy[1]+1][xy[0]-1] = j
                                    new_layer[xy[1]+2][xy[0]-1] = j
                                    new_layer[xy[1]+3][xy[0]-1] = j
                                    new_layer[xy[1]][xy[0]+1] = 0
                                    new_layer[xy[1]+1][xy[0]+1] = 0
                                    new_layer[xy[1]+2][xy[0]+1] = 0
                                    new_layer[xy[1]+3][xy[0]+1] = 0
                                    space_flag = 1
                        elif dir == 90:
                            if xy[0]-1>-1:
                                if new_layer[xy[1]][xy[0]-1] == 0 and new_layer[xy[1]+1][xy[0]-1] == 0:
                                    new_layer[xy[1]][xy[0]-1] = j
                                    new_layer[xy[1]+1][xy[0]-1] = j
                                    new_layer[xy[1]][xy[0]+3] = 0
                                    new_layer[xy[1]+1][xy[0]+3] = 0
                                    space_flag = 1
                    elif n == 3:
                        if dir == 90:
                            if xy[1]-1>-1:
                                if new_layer[xy[1]-1][xy[0]] == 0 and new_layer[xy[1]-1][xy[0]+1] == 0 and new_layer[xy[1]-1][xy[0]+2] == 0 and new_layer[xy[1]-1][xy[0]+3] == 0:
                                    new_layer[xy[1]-1][xy[0]] = j
                                    new_layer[xy[1]-1][xy[0]+1] = j
                                    new_layer[xy[1]-1][xy[0]+2] = j
                                    new_layer[xy[1]-1][xy[0]+3] = j
                                    new_layer[xy[1]+1][xy[0]] = 0
                                    new_layer[xy[1]+1][xy[0]+1] = 0
                                    new_layer[xy[1]+1][xy[0]+2] = 0
                                    new_layer[xy[1]+1][xy[0]+3] = 0
                                    space_flag = 1
                        elif dir == 0:
                            if xy[1]-1>-1:
                                if new_layer[xy[1]-1][xy[0]] == 0 and new_layer[xy[1]-1][xy[0]+1] == 0:
                                    new_layer[xy[1]-1][xy[0]] = j
                                    new_layer[xy[1]-1][xy[0]+1] = j
                                    new_layer[xy[1]+3][xy[0]] = 0
                                    new_layer[xy[1]+3][xy[0]+1] = 0
                                    space_flag = 1

                    if space_flag==1:
                        old_flag = 0
                        for k in range(0,len(final_final_layers)):
                            if layers_match(new_layer,final_final_layers[k]):
                                old_flag = 1
                        if old_flag == 0:
                            new_deviation = compare_layers(layer,new_layer)
                            if new_deviation<deviation:
                                final_final_layers[i] = copy.deepcopy(new_layer)
                                change_flag = 1
                            elif new_deviation == deviation:
                                final_final_layers.append(copy.deepcopy(new_layer))
                                change_flag = 1
        if change_flag == 0:
            break

    # re decimate
    min_deviation = 32*16
    deviation = []
    for i in range(0,len(final_final_layers)):
        deviation.append(compare_layers(layer,final_final_layers[i]))
        if deviation[i] < min_deviation:
            min_deviation = deviation[i]
        print(i,' deviation: ',deviation[i])

    final_final_final_layers = []
    for i in range(0,len(final_final_layers)):
        if deviation[i]==min_deviation:
            final_final_final_layers.append(final_final_layers[i])

    return final_final_final_layers

def rebrick_from_dist(layer):
    """rebrick but from a probability distribution"""
    layers = []

    return layers

def compare_layers(layer1,layer2):
    """count number of differences between 2 layers"""
    deviation = 0
    for y in range(0,16):
        for x in range(0,32):
            if (layer1[y][x] == 0 and layer2[y][x] != 0) or (layer1[y][x] != 0 and layer2[y][x] == 0):
                deviation+=1
    return deviation

def recursive_populate_layer_xy(layer,next_brick_id=2,layer_number=0):
    """populate layer by turning so1's in groups of 2x4"""
    print('layer ',layer_number,' started')
    layers = [copy.deepcopy(layer)]
    brick_id = next_brick_id
    for y in range(0,16):
        for x in range(0,32):
            if layers[0][y][x] == 1:
                flag0 = 0
                flag90 = 0
                for i in range(0,2):
                    for j in range(0,4):
                        if y+j>15 or x+i>31:
                            flag0 = 1
                        elif layers[0][y+j][x+i] > 1:
                            flag0 = 1
                        if y+i>15 or x+j>31:
                            flag90 = 1
                        elif layers[0][y+i][x+j] > 1:
                            flag90 = 1
                if flag0 == 0:
                    if flag90 == 0:
                        new_layer = copy.deepcopy(layers[0])
                        new_id = brick_id
                        for i in range(0,2):
                            for j in range(0,4):
                                new_layer[y+i][x+j] = new_id
                        new_id+=1
                        new_layers = recursive_populate_layer_xy(new_layer,new_id,layer_number+1)
                        for k in range(0,len(new_layers)):
                            layers.append(new_layers[k])
                    for i in range(0,2):
                        for j in range(0,4):
                            layers[0][y+j][x+i] = brick_id
                    brick_id+=1
                elif flag90 == 0:
                    for i in range(0,2):
                        for j in range(0,4):
                            layers[0][y+i][x+j] = brick_id
                    brick_id+=1
    print('recursive layer',layer_number,' finished')
    return layers

def recursive_populate_layer_nxy(layer,next_brick_id=2,layer_number=0):
    """populate layer by turning so1's in groups of 2x4"""
    print('layer ',layer_number,' started')
    layers = [copy.deepcopy(layer)]
    brick_id = next_brick_id
    for y in range(0,16):
        for x in range(31,-1,-1):
            if layers[0][y][x] == 1:
                flag0 = 0
                flag90 = 0
                for i in range(0,2):
                    for j in range(0,4):
                        if y+j>15 or x-i<0:
                            flag0 = 1
                        elif layers[0][y+j][x-i] > 1:
                            flag0 = 1
                        if y+i>15 or x-j<0:
                            flag90 = 1
                        elif layers[0][y+i][x-j] > 1:
                            flag90 = 1
                if flag0 == 0:
                    if flag90 == 0:
                        new_layer = copy.deepcopy(layers[0])
                        new_id = brick_id
                        for i in range(0,2):
                            for j in range(0,4):
                                new_layer[y+i][x-j] = new_id
                        new_id+=1
                        new_layers = recursive_populate_layer_nxy(new_layer,new_id,layer_number+1)
                        for k in range(0,len(new_layers)):
                            layers.append(new_layers[k])
                    for i in range(0,2):
                        for j in range(0,4):
                            layers[0][y+j][x-i] = brick_id
                    brick_id+=1
                elif flag90 == 0:
                    for i in range(0,2):
                        for j in range(0,4):
                            layers[0][y+i][x-j] = brick_id
                    brick_id+=1
    print('recursive layer',layer_number,' finished')
    return layers

def recursive_populate_layer_xny(layer,next_brick_id=2,layer_number=0):
    """populate layer by turning so1's in groups of 2x4"""
    print('layer ',layer_number,' started')
    layers = [copy.deepcopy(layer)]
    brick_id = next_brick_id
    for y in range(15,-1,-1):
        for x in range(0,32):
            if layers[0][y][x] == 1:
                flag0 = 0
                flag90 = 0
                for i in range(0,2):
                    for j in range(0,4):
                        if y-j<0 or x+i>31:
                            flag0 = 1
                        elif layers[0][y-j][x+i] > 1:
                            flag0 = 1
                        if y-i<0 or x+j>31:
                            flag90 = 1
                        elif layers[0][y-i][x+j] > 1:
                            flag90 = 1
                if flag0 == 0:
                    if flag90 == 0:
                        new_layer = copy.deepcopy(layers[0])
                        new_id = brick_id
                        for i in range(0,2):
                            for j in range(0,4):
                                new_layer[y-i][x+j] = new_id
                        new_id+=1
                        new_layers = recursive_populate_layer_xny(new_layer,new_id,layer_number+1)
                        for k in range(0,len(new_layers)):
                            layers.append(new_layers[k])
                    for i in range(0,2):
                        for j in range(0,4):
                            layers[0][y-j][x+i] = brick_id
                    brick_id+=1
                elif flag90 == 0:
                    for i in range(0,2):
                        for j in range(0,4):
                            layers[0][y-i][x+j] = brick_id
                    brick_id+=1
    print('recursive layer',layer_number,' finished')
    return layers

def recursive_populate_layer_nxny(layer,next_brick_id=2,layer_number=0):
    """populate layer by turning so1's in groups of 2x4"""
    print('layer ',layer_number,' started')
    layers = [copy.deepcopy(layer)]
    brick_id = next_brick_id
    for y in range(15,-1,-1):
        for x in range(31,-1,-1):
            if layers[0][y][x] == 1:
                flag0 = 0
                flag90 = 0
                for i in range(0,2):
                    for j in range(0,4):
                        if y-j<0 or x-i<0:
                            flag0 = 1
                        elif layers[0][y-j][x-i] > 1:
                            flag0 = 1
                        if y-i<0 or x-j<0:
                            flag90 = 1
                        elif layers[0][y-i][x-j] > 1:
                            flag90 = 1
                if flag0 == 0:
                    if flag90 == 0:
                        new_layer = copy.deepcopy(layers[0])
                        new_id = brick_id
                        for i in range(0,2):
                            for j in range(0,4):
                                new_layer[y-i][x-j] = new_id
                        new_id+=1
                        new_layers = recursive_populate_layer_nxny(new_layer,new_id,layer_number+1)
                        for k in range(0,len(new_layers)):
                            layers.append(new_layers[k])
                    for i in range(0,2):
                        for j in range(0,4):
                            layers[0][y-j][x-i] = brick_id
                    brick_id+=1
                elif flag90 == 0:
                    for i in range(0,2):
                        for j in range(0,4):
                            layers[0][y-i][x-j] = brick_id
                    brick_id+=1
    print('recursive layer',layer_number,' finished')
    return layers

def spiral_scan(x,y):
    """generate ranges for spiral scan pattern"""
    xrange = range(0,32)
    yrange = range(0,16)
    dir = 0
    return xrange,yrange,dir

def recursive_populate_layer_perim(layer,next_brick_id=2,layer_number=0,x_start=0,y_start=0):
    """populate layer by turning so1's in groups of 2x4"""
    print('layer ',layer_number,' started')
    layers = [copy.deepcopy(layer)]
    brick_id = next_brick_id
    x = x_start
    y = y_start
    while not(x==7 and y==8):
        xrange,yrange,dir = spiral_scan(x,y)
        for y in yrange:
            for x in xrange:
                if layers[0][y][x] == 1:
                    flag0 = 0
                    flag90 = 0
                    for i in range(0,2):
                        for j in range(0,4):
                            if dir == 0:
                                if y+j>15 or x+i>31:
                                    flag0 = 1
                                elif layers[0][y+j][x+i] > 1:
                                    flag0 = 1
                                if y+i>15 or x+j>31:
                                    flag90 = 1
                                elif layers[0][y+i][x+j] > 1:
                                    flag90 = 1
                            elif dir == 1:
                                if y+j>15 or x-i<0:
                                    flag0 = 1
                                elif layers[0][y+j][x-i] > 1:
                                    flag0 = 1
                                if y+i>15 or x-j<0:
                                    flag90 = 1
                                elif layers[0][y+i][x-j] > 1:
                                    flag90 = 1
                            elif dir == 2:
                                if y-j<0 or x+i>31:
                                    flag0 = 1
                                elif layers[0][y-j][x+i] > 1:
                                    flag0 = 1
                                if y-i<0 or x+j>31:
                                    flag90 = 1
                                elif layers[0][y-i][x+j] > 1:
                                    flag90 = 1
                            elif dir == 3:
                                if y-j<0 or x-i<0:
                                    flag0 = 1
                                elif layers[0][y-j][x-i] > 1:
                                    flag0 = 1
                                if y-i<0 or x-j<0:
                                    flag90 = 1
                                elif layers[0][y-i][x-j] > 1:
                                    flag90 = 1
                    if flag0 == 0:
                        if flag90 == 0:
                            new_layer = copy.deepcopy(layers[0])
                            new_id = brick_id
                            for i in range(0,2):
                                for j in range(0,4):
                                    if dir == 0:
                                        new_layer[y+i][x+j] = new_id
                                    elif dir == 1:
                                        new_layer[y+i][x-j] = new_id
                                    elif dir == 2:
                                        new_layer[y-i][x+j] = new_id
                                    elif dir == 3:
                                        new_layer[y-i][x-j] = new_id
                            new_id+=1
                            new_layers = recursive_populate_layer_perim(new_layer,new_id,layer_number+1,x,y)
                            for k in range(0,len(new_layers)):
                                layers.append(new_layers[k])
                        for i in range(0,2):
                            for j in range(0,4):
                                if dir == 0:
                                    layers[0][y+j][x+i] = brick_id
                                elif dir == 1:
                                    layers[0][y+j][x-i] = brick_id
                                elif dir == 2:
                                    layers[0][y-j][x+i] = brick_id
                                elif dir == 3:
                                    layers[0][y-j][x-i] = brick_id
                        brick_id+=1
                    elif flag90 == 0:
                        for i in range(0,2):
                            for j in range(0,4):
                                if dir == 0:
                                    layers[0][y+i][x+j] = brick_id
                                elif dir == 1:
                                    layers[0][y+i][x-j] = brick_id
                                elif dir == 2:
                                    layers[0][y-i][x+j] = brick_id
                                elif dir == 3:
                                    layers[0][y-i][x-j] = brick_id
                        brick_id+=1
    print('recursive layer',layer_number,' finished')
    return layers

def layers_match(layer1,layer2):
    for y in range(0,16):
        for x in range(0,32):
            if layer1[y][x] < 2 and layer2[y][x] >= 2:
                return False
            if layer1[y][x] >= 2 and layer2[y][x] < 2:
                return False
            if y<15 and x<29:
                if (layer1[y][x]==layer1[y+1][x+3] and layer1[y][x]>=2) and (layer2[y][x]!=layer2[y+1][x+3] or layer2[y][x]<2):
                    return False
            if y<13 and x<31:
                if (layer1[y][x]==layer1[y+3][x+1] and layer1[y][x]>=2) and (layer2[y][x]!=layer2[y+3][x+1] or layer2[y][x]<2):
                    return False
    return True

def dilate(layer):
    new_layer = copy.deepcopy(layer)
    for y in range(0,16):
        for x in range(0,32):
            if new_layer[y][x] == 0:
                if y>0 and x>0:
                    if layer[y-1][x-1] > 0:
                        new_layer[y][x] = 1
                if y>0:
                    if layer[y-1][x] > 0:
                        new_layer[y][x] = 1
                if x>0:
                    if layer[y][x-1] > 0:
                        new_layer[y][x] = 1
                if y<15 and x<31:
                    if layer[y+1][x+1] > 0:
                        new_layer[y][x] = 1
                if y<15:
                    if layer[y+1][x] > 0:
                        new_layer[y][x] = 1
                if x<31:
                    if layer[y][x+1] > 0:
                        new_layer[y][x] = 1
                if y>0 and x<31:
                    if layer[y-1][x+1] > 0:
                        new_layer[y][x] = 1
                if y<15 and x>0:
                    if layer[y+1][x-1] > 0:
                        new_layer[y][x] = 1
    return new_layer

def erode(layer):
    new_layer = copy.deepcopy(layer)
    for y in range(0,16):
        for x in range(0,32):
            if new_layer[y][x] > 0:
                if y>0 and x>0:
                    if layer[y-1][x-1] == 0:
                        new_layer[y][x] = 0
                if y>0:
                    if layer[y-1][x] == 0:
                        new_layer[y][x] = 0
                if x>0:
                    if layer[y][x-1] == 0:
                        new_layer[y][x] = 0
                if y<15 and x<31:
                    if layer[y+1][x+1] == 0:
                        new_layer[y][x] = 0
                if y<15:
                    if layer[y+1][x] == 0:
                        new_layer[y][x] = 0
                if x<31:
                    if layer[y][x+1] == 0:
                        new_layer[y][x] = 0
                if y>0 and x<31:
                    if layer[y-1][x+1] == 0:
                        new_layer[y][x] = 0
                if y<15 and x>0:
                    if layer[y+1][x-1] == 0:
                        new_layer[y][x] = 0
    return new_layer