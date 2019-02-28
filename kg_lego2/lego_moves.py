#!/usr/bin/env python
# Motion-planning functions for use with kg398_lego tasks
import serial
import socket
import time
import random
import copy
import math
import numpy as np
from math import pi

import waypoints as wp

# ---will only work with windows--- (only used for manual calibration)
import msvcrt

# gripper states
EMPTY = 0
X4 = 1
X2 = 2

#---------------------------------------------------------------------------------#
#-----------------------------------CALIBRATION-----------------------------------#
#---------------------------------------------------------------------------------#

def keyboard_control(robot):
    print("Starting manual point locating, press 'e' to end\nmove in x: 'w' and 's'\nmove in y: 'a' and 'd'\nmove in z: 'r' and 'l'")
    ipt = 'q'
    while ipt!='e':
        ipt = bytes.decode(msvcrt.getch())
        #print('\n'+ipt)
        if ipt=='w':
            robot.translatel_rel([0.0005,0,0,0,0,0])
        if ipt=='s':
            robot.translatel_rel([-0.0005,0,0,0,0,0])
        if ipt=='d':
            robot.translatel_rel([0,-0.0005,0,0,0,0])
        if ipt=='a':
            robot.translatel_rel([0,0.0005,0,0,0,0])
        if ipt=='r':
            robot.translatel_rel([0,0,0.0005,0,0,0])
        if ipt=='l':
            robot.translatel_rel([0,0,-0.0005,0,0,0])
    print("Location confirmed: {}\n".format(robot.getl()))
    return robot.getl()

def calibrate(robot):
    robot.set_tcp(wp.cal_lego_tcp)

    demand_pose = copy.deepcopy(wp.grid_0_1)
    demand_pose[2]+=0.01
    robot.movejl(demand_pose)
    grid_0_1 = keyboard_control(robot)
    grid_0_1_joints = robot.getj()
    robot.translatel_rel([0,0,0.01])
    robot.home()

    demand_pose = copy.deepcopy(wp.grid_30_1)
    demand_pose[2]+=0.01
    robot.movejl(demand_pose)
    grid_30_1 = keyboard_control(robot)
    grid_30_1_joints = robot.getj()
    robot.translatel_rel([0,0,0.01])
    robot.home()

    demand_pose = copy.deepcopy(wp.grid_30_13)
    demand_pose[2]+=0.01
    robot.movejl(demand_pose)
    grid_30_13 = keyboard_control(robot)
    grid_30_13_joints = robot.getj()
    robot.translatel_rel([0,0,0.01])
    robot.home()

    demand_pose = copy.deepcopy(wp.grid_0_13)
    demand_pose[2]+=0.01
    robot.movejl(demand_pose)
    grid_0_13 = keyboard_control(robot)
    grid_0_13_joints = robot.getj()
    robot.translatel_rel([0,0,0.01])
    robot.home()

    demand_pose = copy.deepcopy(wp.grid_30_1_10)
    demand_pose[2]+=0.01
    robot.movejl(demand_pose)
    grid_30_1_10 = keyboard_control(robot)
    grid_30_1_10_joints = robot.getj()
    robot.translatel_rel([0,0,0.01])
    robot.home()
    
    print("grid_0_1 =",grid_0_1)
    print("grid_0_1_joints =",grid_0_1_joints)
    print("grid_30_1 =",grid_30_1)
    print("grid_30_1_joints =",grid_30_1_joints)
    print("grid_30_13 =",grid_30_13)
    print("grid_30_13_joints =",grid_30_13_joints)
    print("grid_0_13 =",grid_0_13)
    print("grid_0_13_joints =",grid_0_13_joints)
    print("grid_30_1_10 =",grid_30_1_10)
    print("grid_30_1_10_joints =",grid_30_1_10_joints)
    
    robot.set_tcp(wp.lego_tcp)
    return

def calibrate_feed(robot):
    robot.set_tcp(wp.cal_lego_tcp)
    hopper = [[0,0,0],[0,0,0]]
    hopper_joints = [[0,0,0],[0,0,0]]

    demand_pose = copy.deepcopy(wp.hopper[0][0])
    demand_pose[2]+=0.02
    robot.movejl(demand_pose)
    hopper[0][0] = keyboard_control(robot)
    hopper_joints[0][0] = robot.getj()
    robot.translatel_rel([0,0,0.1])

    demand_pose = copy.deepcopy(wp.hopper[0][1])
    demand_pose[2]+=0.02
    robot.movejl(demand_pose)
    hopper[0][1] = keyboard_control(robot)
    hopper_joints[0][1] = robot.getj()
    robot.translatel_rel([0,0,0.1])

    demand_pose = copy.deepcopy(wp.hopper[0][2])
    demand_pose[2]+=0.02
    robot.movejl(demand_pose)
    hopper[0][2] = keyboard_control(robot)
    hopper_joints[0][2] = robot.getj()
    robot.translatel_rel([0,0,0.1])

    demand_pose = copy.deepcopy(wp.hopper[1][0])
    demand_pose[2]+=0.02
    robot.movejl(demand_pose)
    hopper[1][0] = keyboard_control(robot)
    hopper_joints[1][0] = robot.getj()
    robot.translatel_rel([0,0,0.1])

    demand_pose = copy.deepcopy(wp.hopper[1][1])
    demand_pose[2]+=0.02
    robot.movejl(demand_pose)
    hopper[1][1] = keyboard_control(robot)
    hopper_joints[1][1] = robot.getj()
    robot.translatel_rel([0,0,0.1])

    demand_pose = copy.deepcopy(wp.hopper[1][2])
    demand_pose[2]+=0.02
    robot.movejl(demand_pose)
    hopper[1][2] = keyboard_control(robot)
    hopper_joints[1][2] = robot.getj()
    robot.translatel_rel([0,0,0.1])
    
    robot.home()
    
    print("hopper = [[",hopper[0][0],",\n",hopper[0][1],",\n",hopper[0][2],"],\n[",
                        hopper[1][0],",\n",hopper[1][1],",\n",hopper[1][2],"]]")

    print("hopper_joints = [[",hopper_joints[0][0],",\n",hopper_joints[0][1],",\n",hopper_joints[0][2],"],\n[",
                               hopper_joints[1][0],",\n",hopper_joints[1][1],",\n",hopper_joints[1][2],"]]")
    
    robot.set_tcp(wp.lego_tcp)
    return

#---------------------------------------------------------------------------------#
#-------------------------------------ASSEMBLY------------------------------------#
#---------------------------------------------------------------------------------#

# Assemble a build que
def assemble(robot,bricks,t=True):
    EE_STATE = EMPTY
    delay = 0
    n = 0
    for i in range(0,len(bricks)):
        # stop after 0,20,40 etc bricks to fill hoppers 
        if i % 20 == 0 and t == True:
            tic = time.time()
            input("Fill hopper and press enter to continue")
            toc = time.time()
            delay+=toc-tic

        # get bricks from feed system
        get_bricks(robot,bricks[i],EE_STATE)

        # grid placing
        master_place(robot,bricks[i])

        # stow excess
        EE_STATE = stow_excess(robot,bricks[i:])

    return delay

def get_bricks(robot,brick,STATE):
    if brick['b']==0:                                      # if 2x4 brick use hopper 0
        if brick['p']==3:                                  # if tool placing method, pick 2 bricks
            if STATE == EMPTY:
                feed_pick(robot)
            feed_pick(robot,stack=2)
        elif (brick['r'] == 0 or brick['r'] == 180) and STATE == EMPTY:
            feed_pick(robot,X=brick['p'])
        elif STATE == EMPTY:
            feed_pick(robot,X=2-brick['p'])

    elif brick['b']==1:                                     # if 2x2 brick use hopper 1
        if STATE == EMPTY:
            feed_pick(robot,X=2,H=1)
        if brick['p'] == 3:
            feed_pick(robot,X=2,H=1,stack=2)

    # home waypoint
    robot.home()
    return

def master_place(robot,brick):
    #2x4 brick
    if brick['b']==0:
        if brick['p']==3:
            if brick['r'] == 0 or brick['r'] == 180:
                grid_place(robot,brick['x'],brick['y']+1,brick['z'],brick['r'],XE=-brick['ye'],YE=brick['xe'],stack=2)
            else:
                grid_place(robot,brick['x']+1,brick['y'],brick['z'],brick['r'],XE=brick['xe'],YE=brick['ye'],stack=2)

        else:
            if brick['r'] == 0 or brick['r'] == 180:
                grid_place(robot,brick['x'],brick['y']+brick['p'],brick['z'],brick['r'],XE=-brick['ye'],YE=brick['xe'],stack=1)
            else:
                grid_place(robot,brick['x']+brick['p'],brick['y'],brick['z'],brick['r'],XE=brick['xe'],YE=brick['ye'],stack=1)

    #2x2 brick
    elif brick['b']==1:
        if brick['p']==3:
            grid_place(robot,brick['x'],brick['y'],brick['z'],brick['r'],XE=brick['xe'],YE=brick['ye'],stack=2)
        else:
            grid_place(robot,brick['x'],brick['y'],brick['z'],brick['r'],XE=brick['xe'],YE=brick['ye'],stack=1)
    return

def stow_excess(robot,input_bricks):
    bricks = list(input_bricks)
    STATE = 0
    if len(bricks) != 1:
        # stowing excess bricks
        if bricks[0]['p']==3:
            if bricks[0]['b'] == 0 and bricks[1]['b'] == 0 and (bricks[1]['p'] == 1 or bricks[1]['p'] == 3):   # if tool placing, don't stow brick if next place can use it
                STATE = X4
            elif bricks[0]['b'] == 1 and bricks[1]['b'] == 1:  
                STATE = X2
            else:
                robot.home()
                feed_place(robot,H=bricks[0]['b'])
    else:
        if bricks[0]['p']==3:
            feed_place(robot,H=bricks[0]['b'])

    # home waypoint
    robot.home()
    return STATE



#---------------------------------------------------------------------------------#
#-----------------------------------DISASSEMBLY-----------------------------------#
#---------------------------------------------------------------------------------#

# Disassemble a build que
def disassemble(robot,bricks,t=True):
    EE_STATE = EMPTY
    delay = 0
    for i in range(0,len(bricks)):                              # pick brick, place in feed system, move up, repeat for whole list
        # stop after 0,20,40 etc bricks to empty hoppers 
        if i % 20 == 0 and t == True:
            tic = time.time()
            input("Empty hopper and press enter to continue")
            toc = time.time()
            delay+=toc-tic

        # pick brick if using tool disassembly
        get_tool(robot,bricks[i],EE_STATE)

        # pick brick from grid
        master_pick(robot,bricks[i])

        # stow bricks
        EE_STATE = stow_bricks(robot,bricks[i:]) 
    return delay

def get_tool(robot,brick,EE_STATE):
    if brick['p'] == 3 and EE_STATE == EMPTY:
        if brick['b'] == 0:
            feed_pick(robot)
        else:
            feed_pick(robot,X=2,H=1)
        robot.home()
    return

def master_pick(robot,brick):
    # pick brick from grid
    # 2x4 brick
    if brick['b'] == 0:
        if brick['p'] == 3:
            if brick['r'] == 0 or brick['r'] == 180:
                grid_pick(robot,brick['x'],brick['y']+1,brick['z'],brick['r'],stack=2)
            else:
                grid_pick(robot,brick['x']+1,brick['y'],brick['z'],brick['r'],stack=2)
        else:
            if brick['r'] == 0 or brick['r'] == 180:
                grid_pick(robot,brick['x'],brick['y']+brick['p'],brick['z'],brick['r'],stack=1)
            else:
                grid_pick(robot,brick['x']+brick['p'],brick['y'],brick['z'],brick['r'],stack=1)

    # 2x2 brick
    elif brick['b'] == 1:
        if brick['p'] == 3:
            grid_pick(robot,brick['x'],brick['y'],brick['z'],brick['r'],stack=2)
        else:
            grid_pick(robot,brick['x'],brick['y'],brick['z'],brick['r'],stack=1)

    # home waypoint
    robot.home()
    return

def stow_bricks(robot,input_bricks):
    bricks = list(input_bricks)
    STATE = 0
    # stow bricks
    if bricks[0]['p'] == 3:
        feed_place2(robot,sH=bricks[0]['b'])

    if len(bricks) != 1:
    # if tool picking next, don't stow brick
        if (bricks[0]['p'] == 3 or bricks[0]['p'] == 1) and bricks[1]['p'] == 3 and bricks[0]['b'] == 0:
            STATE = X4
        elif bricks[1]['p'] == 3 and bricks[0]['b'] == 1:
            STATE = X2
        else:
            feed_place(robot,H=bricks[0]['b'])
    else:
        feed_place(robot,H=bricks[0]['b'])

    # home waypoint
    robot.home()
    return STATE



#---------------------------------------------------------------------------------#
#-----------------------------------FEED SYSTEM-----------------------------------#
#---------------------------------------------------------------------------------#

# Pick from feed system
def feed_pick(robot,X=1,H=0,stack=1):
    demand_Pose = copy.deepcopy(wp.hopper[H][X])

    if stack == 1:                                              # normal picking
        demand_Pose[2] += 0.019
        robot.movejl(demand_Pose)

        robot.translatel_rel([0,0,-0.02])

        robot.close_gripper(0)                             # close grabber
        robot.close_gripper(0)                             # close grabber
        robot.close_gripper(0)
        robot.close_gripper(0)
        robot.close_gripper(2)
        robot.close_gripper(2)
    
        robot.translatejl_rel([0,0,0.04])

    elif stack == 2:                                            # run after normal picking to pick a second brick
        demand_Pose[2] += 0.039
        robot.movejl(demand_Pose)

        robot.translatel_rel([0,0,-0.04+0.008],vel=0.25)

        robot.translatel_rel([0.0005,0.0005,0])
        
        robot.translatel_rel([0.0005,0.0005,0.005])

        robot.translatel_rel([-0.001,-0.001,0.035-0.008])

    return


# function for disassembling a stack of 2 into the feed system using the feed system
def feed_place2(robot,sH=0):
    # separate stack by placing in pick position
    demand_Pose = copy.deepcopy(wp.hopper[0][1])

    demand_Pose[2] += 0.038
    robot.movejl(demand_Pose)        # move above brick

    robot.translatel_rel([0,0,-0.0205])

    robot.set_tcp(wp.lego_tcp_1brick)
    robot.movel_tool([0,0,0,0,-15*pi/180.0,0])       # rotate grabber
    robot.set_tcp(wp.lego_tcp)

    demand_Pose = robot.getl()
    demand_Pose[2] += 0.08
    robot.movel(demand_Pose)

    feed_place(robot,H=sH)

    demand_Pose = copy.deepcopy(wp.hopper[0][1])

    demand_Pose[2] += 0.0285
    robot.movejl(demand_Pose)         # move above brick

    robot.translatel_rel([0,0,-0.02])

    robot.close_gripper(0)                             # close grabber
    robot.close_gripper(0)                             # close grabber
    robot.close_gripper(0)
    robot.close_gripper(0)
    robot.close_gripper(2)
    robot.close_gripper(2)

    demand_Pose = robot.getl()
    demand_Pose[0] = wp.hopper[0][0][0]
    demand_Pose[1] = wp.hopper[0][0][1]
    robot.movel(demand_Pose)

    robot.set_tcp(wp.lego_tcp_1brick)
    robot.movel_tool([0,0,0,0,-30*pi/180.0,0])       # rotate grabber
    robot.set_tcp(wp.lego_tcp)

    robot.translatel_rel([0,0,0.08])

    #feed_place(c,ser_ee,H=sH)
    return


# Place in feed system
def feed_place(robot,H=0):
    demand_Joints = copy.deepcopy(wp.hopper_stow_wp_joints[H])
    demand_Pose = copy.deepcopy(wp.hopper_stow[H])
    
    robot.movej(demand_Joints,vel=1.2)

    robot.movel(demand_Pose)
    
    robot.open_gripper(0)
    robot.open_gripper(0)
    robot.open_gripper(0)
    robot.open_gripper(0)
    robot.open_gripper(1)                                       # open gripper
    robot.close_gripper(0)
    robot.close_gripper(0)
    robot.close_gripper(0)
    robot.close_gripper(0)

    robot.translatejl_rel([0.003,0,0])
    
    robot.set_tcp(wp.lego_tcp_0brick)
    robot.movel_tool([0,0,0,0,-15*pi/180.0,0])       # rotate grabber
    robot.set_tcp(wp.lego_tcp)

    robot.translatejl_rel([-0.003,0,0])

    robot.translatejl_rel([0,-0.02,0])

    robot.home(vel=1.2)
    return





#---------------------------------------------------------------------------------#
#-------------------------------------WORKSPACE-----------------------------------#
#---------------------------------------------------------------------------------#

# Pick from a grid location
def grid_pick(robot,x,y,z,r,stack=1):
    demand_Joints = grid_pos(robot,x,y,z+1+stack,r)
    robot.movej(demand_Joints)        # move above brick

    #ic.super_serial_send(ser_ee,"G",51)

    demand_Joints = grid_pos(robot,x,y,z-0.1+stack,r)
    robot.movej(demand_Joints)

    demand_Joints = grid_pos(robot,x,y,z-1+stack,r)
    robot.movej(demand_Joints)

    if stack == 1:
        robot.close_gripper(0)                             # close grabber
        robot.close_gripper(0)                             # close grabber
        robot.close_gripper(0)
        robot.close_gripper(0)
        robot.close_gripper(2)
        robot.close_gripper(2)

        robot.set_tcp(wp.lego_tcp_1brick)
    elif stack == 2:
        robot.set_tcp(wp.lego_tcp_2brick)
    robot.movel_tool([0,0,0,0,-15*pi/180.0,0])              # rotate grabber
    robot.set_tcp(wp.lego_tcp)

    robot.translatel_rel([0,0,0.02])
    
    demand_Joints = grid_pos(robot,x,y,z+1+stack,r)
    robot.movej(demand_Joints)     # move back up

# Place in a grid location
def grid_place(robot,x,y,z,r,XE=0,YE=0,stack=1):
    alpha = 0.3
    XE = alpha*XE
    YE = alpha*YE
    
    demand_Joints = grid_pos(robot,x+XE,y+YE,z+1+stack,r)
    robot.movej(demand_Joints)    # move above location

    demand_Joints = grid_pos(robot,x,y,z-0.5+stack,r)
    robot.movej(demand_Joints)

    demand_Joints = grid_pos(robot,x,y,z-1+stack,r)
    robot.movej(demand_Joints)

    if stack == 1:                                                  # if normal placing, release brick
        robot.open_gripper(0)
        robot.open_gripper(0)
        robot.open_gripper(0)
        robot.open_gripper(0)
        robot.open_gripper(1)                                       # open gripper

        robot.set_tcp(wp.lego_tcp_0brick)
        robot.movel_tool([0,0,0,0,-15*pi/180.0,0])             # rotate grabber

    elif stack == 2:                                                # if tool placing, pick top brick
        robot.set_tcp(wp.lego_tcp_1brick)
        robot.movel_tool([0,0,0,0,-15*pi/180.0,0])             # rotate grabber

    robot.set_tcp(wp.lego_tcp)

    robot.translatel_rel([0,0,0.003])
    demand_Joints = grid_pos(robot,x,y,z+1+stack,r)
    robot.movej(demand_Joints)               # move back up
    return

# Converts grid position to robot co-ordinates
# Uses linear interpolation of calibration points in ur_waypoints
# Returns demand pose in joint space
def grid_pos(robot,x,y,z,r):
    # x:0-31
    # y:0-15
    # z:0-31
    # r:0/90
    nx = 30
    ny = 12
    nz = 9

    # dx = {"x": (wp.grid_30_1['x']-wp.grid_0_1['x'])/nx, "y": (wp.grid_30_1['y']-wp.grid_0_1['y'])/nx, "z": (wp.grid_30_1['z']-wp.grid_0_1['z'])/nx, "rx": 0, "ry": 0, "rz": 0}
    dy1 = [(wp.grid_0_13[0]-wp.grid_0_1[0])/ny,     (wp.grid_0_13[1]-wp.grid_0_1[1])/ny,        (wp.grid_0_13[2]-wp.grid_0_1[2])/ny,        0,  0,  0]
    dy2 = [(wp.grid_30_13[0]-wp.grid_30_1[0])/ny,   (wp.grid_30_13[1]-wp.grid_30_1[1])/ny,      (wp.grid_30_13[2]-wp.grid_30_1[2])/ny,      0,  0,  0]
    dz  = [(wp.grid_30_1_10[0]-wp.grid_30_1[0])/nz, (wp.grid_30_1_10[1]-wp.grid_30_1[1])/nz,    (wp.grid_30_1_10[2]-wp.grid_30_1[2])/nz,    0,  0,  0]

    y1_Pose = [wp.grid_0_1[0] + (y-1)*dy1[0] + z*dz[0], 
               wp.grid_0_1[1] + (y-1)*dy1[1] + z*dz[1], 
               wp.grid_0_1[2] + (y-1)*dy1[2] + z*dz[2], 
               wp.grid_0_1[3], wp.grid_0_1[4], wp.grid_0_1[5]]

    y2_Pose = [wp.grid_30_1[0] + (y-1)*dy2[0] + z*dz[0], 
               wp.grid_30_1[1] + (y-1)*dy2[1] + z*dz[1], 
               wp.grid_30_1[2] + (y-1)*dy2[2] + z*dz[2], 
               wp.grid_30_1[3], wp.grid_0_1[4], wp.grid_0_1[5]]

    grid_Pose = [((nx-x)*y1_Pose[0] + x*y2_Pose[0])/nx, 
                 ((nx-x)*y1_Pose[1] + x*y2_Pose[1])/nx, 
                 ((nx-x)*y1_Pose[2] + x*y2_Pose[2])/nx, 
                 wp.grid_0_1[3], wp.grid_0_1[4], wp.grid_0_1[5]]


    calculated_Joints = robot.get_inverse_kin(grid_Pose)      # uses UR inverse kinematics solver to get joint positions, then add rotation for brick orienation
    calculated_Joints[5]+=r*pi/180.0
    if calculated_Joints[5] > 1.5*pi:
        calculated_Joints[5]-=2*pi

    return calculated_Joints
