#!/usr/bin/python

from scipy.stats import zipf
import numpy as np
import math
import random as rand



def create_reseau(trace,output):

	reseau = []

	for ligne in trace:

		decoupe = ligne.split()
		#creation des noeuds
		if decoupe[0] not in reseau:
			reseau.append(decoupe[0])
			output.write("set (n%s) [$ns node]\n" %decoupe[0])

		if decoupe[1] not in reseau:
			reseau.append(decoupe[1])
			output.write("set (n%s) [$ns node]\n" %decoupe[1])

		#creation des liens duplex
		output.write("$ns duplex-link $(n%s) $(n%s) %sMb %sms DropTail\n" %(decoupe[0], decoupe[1], decoupe[2], decoupe[3]))
		#monitoring des files d'attentes par lien
		output.write("set (monitor_queue%s-%s) [$ns monitor-queue $(n%s) $(n%s) (queue%s-%s) 1]\n" %(decoupe[0], decoupe[1], decoupe[0], decoupe[1], decoupe[0], decoupe[1]))
		output.write("set (monitor_queue%s-%s) [$ns monitor-queue $(n%s) $(n%s) (queue%s-%s) 1]\n" %(decoupe[1], decoupe[0], decoupe[1], decoupe[0], decoupe[1], decoupe[0]))
		output.write("$ns at 300 \"record %s %s\"\n" %(decoupe[0], decoupe[1]))
		output.write("\n")


def mult(traf):
	mult=10
	boolean=True
	if traf < mult:
		return 1
	while boolean:
		if traf < mult*10:
			boolean=False
		else:
			mult = mult*10
	return mult/10


def create_trafic(trace,output,on,off,forme,debut,fin,nb_flux):


	output.write("Agent/TCP set packetSize_ 1500\n")
	output.write("Agent/TCP set windowSize_ 75\n")
	output.write("Agent/UDP set packetSize_ 1500\n")

	for ligne in trace:

		decoupe = ligne.split()
		qtite = int(decoupe[2])

		pareto = int((0.85*qtite)//1)
		ftp = int(qtite-pareto)


		debit_temp = pareto * 2 / (fin + fin/9)

		if debit_temp == 0:
				debit = debit_temp * 1000
		else:
			debit = debit_temp * 100

		output.write("set (sudp%s-%s) [new Agent/UDP]\n" %(decoupe[0], decoupe[1]))
		output.write("$ns attach-agent $(n%s) $(sudp%s-%s)\n" %(decoupe[1], decoupe[0], decoupe[1]))
		output.write("set (udp%s-%s) [new Agent/UDP]\n" %(decoupe[0], decoupe[1]))
		output.write("$ns attach-agent $(n%s) $(udp%s-%s)\n" %(decoupe[0], decoupe[0], decoupe[1]))
		output.write("$ns connect $(udp%s-%s) $(sudp%s-%s)\n" %(decoupe[0], decoupe[1], decoupe[0], decoupe[1]))

		output.write("set (par%s-%s) [new Application/Traffic/Pareto]\n" %(decoupe[0], decoupe[1]))
		output.write("$(par%s-%s) set packetSize_ 1500\n" %(decoupe[0], decoupe[1]))
		output.write("$(par%s-%s) set burst_time_ %sms\n" %(decoupe[0], decoupe[1], on))
		output.write("$(par%s-%s) set idle_time_ %sms\n" %(decoupe[0], decoupe[1], off))
		output.write("$(par%s-%s) set shape_ %s\n" %(decoupe[0], decoupe[1], forme))
		output.write("$(par%s-%s) set rate_ %sk\n" %(decoupe[0], decoupe[1], debit))
		output.write("$(par%s-%s) attach-agent $(udp%s-%s)\n" %(decoupe[0], decoupe[1], decoupe[0], decoupe[1]))
		output.write("$ns at %s \"$(par%s-%s) start\"\n" %(debut, decoupe[0], decoupe[1]))
		output.write("$ns at %s \"$(par%s-%s) stop\"\n\n" %(fin, decoupe[0], decoupe[1]))


		random = 0
		k = 0

		dec = mult(ftp)

		while random < ftp:
			sent = zipf.rvs(forme) * dec
			inst = int(rand.uniform(debut,fin))
			if sent == 0:
				print "\nValeur nulle envoyee : %s\n" %(sent)

			if sent < ftp and sent > 0:
				if k > nb_flux-1:
					output.write("$ns at %s \"$(tcp%s-%s-%s) send %s\"\n\n" %(inst, decoupe[0], decoupe[1], k%nb_flux, sent))
				else:
					output.write("set (tcp%s-%s-%s) [new Agent/TCP]\n" %(decoupe[0], decoupe[1], k))
					output.write("$ns attach-agent $(n%s) $(tcp%s-%s-%s)\n" %(decoupe[0], decoupe[0], decoupe[1], k))
					output.write("set (stcp%s-%s-%s) [new Agent/TCPSink]\n" %(decoupe[0], decoupe[1], k))
					output.write("$ns attach-agent $(n%s) $(stcp%s-%s-%s)\n" %(decoupe[1], decoupe[0], decoupe[1], k))
					output.write("$ns connect $(tcp%s-%s-%s) $(stcp%s-%s-%s)\n" %(decoupe[0], decoupe[1], k, decoupe[0], decoupe[1], k))
					output.write("$ns at %s \"$(tcp%s-%s-%s) send %sk\"\n\n" %(inst, decoupe[0], decoupe[1], k, sent))

				random += sent
				k+=1


topo = open("topo.top","r")
traf = open("traff.traf","r")
out = open("geant.tcl","w")

out.write("set ns [new Simulator]\n")
out.write("set loss [open pertes.tr w]\n\n")

out.write("proc finish {} {\n")
out.write("    global ns loss\n")
out.write("    $ns flush-trace\n")
out.write("    close $loss\n")
out.write("    exit 0\n")
out.write("}\n\n")

out.write("Node instproc getidnode {} {\n")
out.write("\t$self instvar id_\n    return \"$id_\"\n}\n\n")

out.write("proc record {i j} {\n")
out.write("\tglobal ns n monitor_queue loss\n")
out.write("\tset now [$ns now]\n")
out.write("\tset from_node [$(n$i) getidnode]\n")
out.write("\tset to_node [$(n$j) getidnode]\n")
out.write("\tset perte1 [$(monitor_queue$i-$j) set pdrops_]\n")
out.write("\tset perte2 [$(monitor_queue$j-$i) set pdrops_]\n")
out.write("\tset depart1 [$(monitor_queue$i-$j) set pdepartures_]\n")
out.write("\tset depart2 [$(monitor_queue$j-$i) set pdrops_]\n")
out.write("\tputs $loss \"$i $j [expr $perte1 + $perte2] [expr $depart1 + $depart2]\"\n")
out.write("}\n\n")

create_reseau(topo, out)

sim_time = 300
create_trafic(traf, out, 500, 500, 2, sim_time*0.10, sim_time*0.90, 20)

out.write("$ns at 300 \"finish\"\n")
out.write("$ns run\n")

topo.close()
traf.close()
out.close()