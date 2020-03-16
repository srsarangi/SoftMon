import sys, os

namemap = {}
def translate(file, func):
	global namemap

	if not file in namemap:
		namemap[file]={}

		if os.path.isfile(file):
			cmd1 = "objdump -d "+file+" > /tmp/pa.dump"
			cmd2 = "objdump -d -C "+file+" > /tmp/pb.dump"

			# print cmd1
			os.system(cmd1)
			os.system(cmd2)
			
			f1 = open("/tmp/pa.dump",'r')
			f2 = open("/tmp/pb.dump",'r')

			for l1 in f1:
				l2 = f2.readline()

				if ">:" in l1:
					name1 = l1.split('<')[1].split('>')[0].split('@@')[0]
					name2 = l2.split('<')[1].split('>')[0].split('@@')[0]
					name2 = name2.replace(' ','')

					namemap[file][name1]=name2

	if func in namemap[file]:
		return namemap[file][func]
	else:
		return ''


f = open(sys.argv[1],'r')
data = {}
for line in f:
	line = line.strip()
	nodeid = int(line.split()[0][2:])
	data[nodeid] = line

f.close()


def getPath(nodeid):
	path = [nodeid]
	while nodeid>0:
		line = data[nodeid]
		l = line.split()
		nodeid = int(l[1][2:])
		path.append(int(l[1][2:]))

	path.reverse()	
	return path	


PATHS = []

f = open(sys.argv[2],'r')
for line in f:
	nodeid = int(line.strip()[2:])
	ll = data[nodeid]
	l = ll.strip().split()
	cost = int(l[3][2:])
	PATHS.append((cost, getPath(nodeid)))
f.close()

thrs = int(sys.argv[3])
file = sys.argv[2].replace('.nodes','.graph')
outfile = sys.argv[2].replace('.nodes','.svg')

if file==sys.argv[2]:
	print "same", file 
	exit()
f = open(file,'w')

maxlen=0
for (cost,path) in PATHS:
	lenp = len(path)
	if lenp>maxlen:
		maxlen = lenp
print "max depth",maxlen

edgelist = []
f.write("digraph{rankdir=LR;\n")
for numcol in range(1,maxlen+1):
	coldic = {}
	for (cost,path) in PATHS:
		
		if len(path) > numcol:

			nid = path[numcol]
			if nid in coldic:
				coldic[nid]+=cost
			else:
				coldic[nid]=cost

	coldiclist = []
	for fnid in coldic:
		coldiclist.append((fnid,coldic[fnid]))

	coldiclist.sort(reverse=True, key=lambda x:x[1])

	for (fnid,cost) in coldiclist:
		ll = data[fnid]
		l = ll.strip().split()
		name = l[5].split('#')[1].replace('.','_')

		parent = data[int(l[1][2:])].strip().split()[5].split('#')
		if len(parent)>1:
			# par = translate(parent[0],parent[1])
			# if not par=='':
			# 	par = parent[1]
			par = parent[1].replace('.','_')
		else:
			par = "root"

		if cost>thrs:
			edge = par+'->'+name+';\n'
			if not edge in edgelist:
				edgelist.append(edge)
				f.write(name+" [style=filled, fillcolor=green];\n")
				f.write(edge)


f.write('}')
f.close()

import os

os.system('dot -Tsvg '+file+' > '+outfile)



