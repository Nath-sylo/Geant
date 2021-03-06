#!/usr/bin/python

import numpy as np

trace = open("pertes.tr","r")

pertes = []
tot = []
for i in range(25):
	pertes.append([i] * 25)

for line in trace:
	e = line.rstrip('\n\r').split(" ")

	if e[0] == 'd':
		pertes[int(e[2])][int(e[3])]+=1


imax = [0]*3
jmax = [0]*3
valmax = [0]*3

for i in range(len(pertes)):
	for j in range(len(pertes[i])):
		if pertes[i][j] > valmax[0]:
			valmax[0] = pertes[i][j]
			imax[0] = i
			jmax[0] = j
		elif pertes[i][j] > valmax[1]:
			valmax[1] = pertes[i][j]
			imax[1] = i
			jmax[1] = j
		elif pertes[i][j] > valmax[2]:
			valmax[2] = pertes[i][j]
			imax[2] = i
			jmax[2] = j


output  = open("info.txt", "w")

output.write("Les 3 liens les \"plus faibles\" sont:\n")
output.write("\t%s-%s avec %s pertes\n" %(imax[0], jmax[0], valmax[0]))
output.write("\t%s-%s avec %s pertes\n" %(imax[1], jmax[1], valmax[1]))
output.write("\t%s-%s avec %s pertes\n" %(imax[2], jmax[2], valmax[2]))
output.write("\n")
output.write("Pourcentage de pertes par liens :\n")
for i in range(26):
	for j in range(i+1,26):
		if ( tot[i][j] + tot[j][i] != 0 ) :
			pourcent = (pertes[i][j]+pertes[j][i]) / (tot[i][j]+tot[j][i])
			dst.write("\tLien %s-%s : %s\n" %(i,j,pourcent))

trace.close()
output.close()