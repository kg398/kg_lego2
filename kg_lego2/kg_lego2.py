import time
import copy
import serial
from math import pi
import numpy
import json
import socket

import waypoints as wp
import kg_robot as kgr
import lego_moves as lm
import file_decoder as fd
import assembly as ass
import disassembly as dis
import collaboration as col
import gui_test as gt


def main():
    print("------------Configuring Burt-------------\r\n")
    burt = 0
    #burt = kgr.kg_robot(ee_port="COM38")
    #burt = kgr.kg_robot(port=30010,db_host="192.168.1.10")
    #burt = kgr.kg_robot(port=30010,db_host="192.168.1.10",ee_port="COM38")
    print("----------------Hi Burt!-----------------\r\n\r\n")

    try:
        while 1:
            ipt = input("cmd: ")
            if ipt == 'close':
                break
            elif ipt == 'home':
                burt.home()

            elif ipt == 't':
                demand_Joints = lm.grid_pos(burt,2,2,1,0)
                burt.movej(demand_Joints)        # move above brick
                burt.set_tcp(wp.lego_tcp_1brick)
                burt.movel_tool([0,0,0,0,-15*pi/180.0,0])       # rotate grabber
                burt.set_tcp(wp.lego_tcp)
                burt.home()

            # high level lego
            elif ipt == 'cal':
                lm.calibrate(burt)
                #lm.calibrate_feed(burt)
            elif ipt == 'a':
                #burt.assemble(filename='example1')
                #fn = input('input filename:')
                #burt.assemble(filename='example3')
                burt.assemble()
            elif ipt == 'd':
                burt.disassemble()

            # collaboration
            elif ipt == 'col':
                model = []
                while(True):
                    human_layer,robot_layers,quit_flag = col.human_layer(model)
                    if quit_flag == True:
                        break
                    model.append(human_layer)
                    model = col.robot_layers(burt,model,robot_layers)
            elif ipt == 'h':
                col.assemble(burt)     #col.assemble takes a model and number of layers for the robot

            else:
                var = int(input("var: "))
                burt.serial_send(ipt,var,True)

    except SystemExit:
        print('Exiting from ui')
    finally:
        print("Goodbye")
        if burt != 0:
            burt.close()
if __name__ == '__main__': main()

