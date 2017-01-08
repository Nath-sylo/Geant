#!/usr/bin/python

import time
import os

timer = open("time.txt", "w")
start = time.time()
os.system("ns geant.tcl")
timer.write("Temps d'execution : %s\n" %(time.time() - start))
timer.close()