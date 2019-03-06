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
        for i in range(0,len(final_layers)):
            nbricks = 0
            deviation = compare_layers(layer,final_layers[i])
            for y in range(0,16):
                for x in range(0,32):
                    if final_layers[i][y][x] > nbricks:
                        nbricks = final_layers[i][y][x]
            for j in range(2,nbricks+1):
                new_layer = copy.deepcopy(final_layers[i])
                for y in range(0,16):
                    for x in range(0,32):
                        if new_layer[y][x] == j:
                            new_layer[y][x] = 0
                old_flag = 0
                for k in range(0,len(final_layers)):
                    if layers_match(new_layer,final_layers[k]):
                        old_flag = 1
                if old_flag == 0:
                    new_deviation = compare_layers(layer,new_layer)
                    if new_deviation<deviation:
                        final_layers[i] = copy.deepcopy(new_layer)
                        change_flag = 1
                    elif new_deviation == deviation:
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

    return final_final_layers

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