import sys, os

Cost = {} # Cost dictionary
lib = ''
f = open(sys.argv[1].replace('-func.out','.func'),'r')
for line in f:
	if line[0]=='@':
		lib = line.split()[1]
	else:
		l = line.strip().split()
		fn = l[3]
		cost = int(l[0])/int(l[1])
		Cost[lib+'#'+fn] = cost
f.close()
print sys.argv[1]
print "  num funcs = ", format(len(Cost),'10d')

f = open(sys.argv[1],'r') # Balance
fnc = {}
fnr = {}
for line in f:
	l = line.strip().split()
	name = l[1]+'#'+l[2]
	if len(l)==4:
		if not name in fnr:
			fnr[name]=0
		fnr[name]+=1
	else:
		if not name in fnc:
			fnc[name]=0
		fnc[name]+=1
f.close()
TR = {}
FNC = set(fnc.keys())
FNR = set(fnr.keys())
FN = FNC.union(FNR)
FNI = FNC.intersection(FNR)
count=0
for fi in FNI:
	if fnc[fi]==fnr[fi]:
		count+=1
	else:
		TR[fi]=True
for fi in FN-FNI:
	TR[fi]=True
print "    balance = ", count,'/',len(FN)

class Node(object):
    def __init__(self):
        self.child  = None
        self.data   = None
        self.name   = None
        self.head   = None
        self.src    = None
        self.mark   = None
        self.count  = None
        self.cost   = None
        self.stcost = None
        self.parent = None

bname = sys.argv[2]
name = 0
root = Node()
root.child = []
root.data = bname
root.name="0"
root.head=""
root.src=True
root.mark = False
root.count = 1
root.cost = 0
root.stcost = 0
root.parent = "-1"
trouble=0
srcnodes = 0

def writeTree(node,f1,f2):
	f1.write("N:"+node.name+' P:'+node.parent+' C:'+str(node.stcost)+' S:'+str(node.cost)+' T:'+str(node.count)+' D:'+node.data+' H:'+'$'.join(node.head)+'\n')
	if node.src and node.stcost>1000000:
		f2.write("N:"+node.name+' P:'+node.parent+' C:'+str(node.stcost)+' S:'+str(node.cost)+' T:'+str(node.count)+' D:'+node.data+' H:'+'$'.join(node.head)+'\n')
	for ch in node.child:
		writeTree(ch,f1,f2)

def graphviz(node,f1):
	global srcnodes
	global trouble
	if node.src:
		if node.stcost>1000000:
			f1.write('"N:'+node.name+'\n'+str(node.stcost)+'" '+"[style=filled, fillcolor=red];\n")
		else:
			f1.write('"N:'+node.name+'\n'+str(node.stcost)+'" '+"[style=filled, fillcolor=green];\n")
	elif node.stcost>1000000 and node.mark:
		f1.write('"N:'+node.name+'\n'+str(node.stcost)+'" '+"[style=filled, fillcolor=yellow];\n")
		
	for ch in node.child:
		if ch.src and not(node.src):
			trouble+=1

		if ch.mark:	
			f1.write('"N:'+node.name+'\n'+str(node.stcost)+'"->"N:'+ch.name+'\n'+str(ch.stcost)+'";\n')
			srcnodes+=1
		graphviz(ch,f1)
	
f = open(sys.argv[1],'r')
fstack=[root]
tail=[]
saved=0
total=0

for line in f:
	l = line.strip().split()
	fname = l[1]+'#'+l[2]
	if not l[-1]=="ret":
		total+=1

	if fname in TR:
		val = '#'.join(l[1:])
		if not val in tail:
			tail.append(val)
	elif l[-1]=="ret":
		fstack.pop()
	else:
		name+=1
		ch = Node()
		ch.name = str(name)
		ch.data = fname
		ch.head = tail
		ch.src = False
		ch.mark = False
		ch.count = 1
		ch.cost = Cost[ch.data]
		ch.stcost = 0
		if bname in ch.data:
			ch.src=True
		for vi in ch.head:
			vii = vi.split('#')
			if len(vii)==2:
				ch.cost += Cost[vi]
				if bname in vii[0]:
					ch.src=True
		tail=[]
		ch.child = []
		found = False
		for ci in fstack[-1].child:
			if ci.data==ch.data:
				found=True
				saved+=1
				for chi in ch.head:
					if not chi in ci.head:
						ci.head.append(chi)
				ci.src = ci.src or ch.src
				ci.cost += ch.cost
				ci.count += 1 
				fstack.append(ci)
				break

		if not found:
			fstack[-1].child.append(ch)
			ch.parent = fstack[-1].name
			fstack.append(ch)
f.close()

def mark(node):
	mk = node.src
	stct = node.cost

	for ch in node.child:
		(m1,ct) = mark(ch)
		if m1:
			mk = True
		stct+=ct	

	node.mark = mk
	node.stcost = stct
	return (mk,stct)

mark(root)

f1 = open(sys.argv[1].replace('.out','.nodes'),'w')
f2 = open(sys.argv[1].replace('.out','.fn'),'w')
writeTree(root,f1,f2)
f1.close()
f2.close()

f1=open(sys.argv[1].replace('.out','.graph'),'w')
f1.write("digraph{rankdir=LR;\n")
graphviz(root,f1)
f1.write('}')
f1.close()

print '  len stack = ', format(len(fstack),'10d')
print ' orig nodes = ', format(total,'10d')
print '  num nodes = ', format(name,'10d')
print 'merge nodes = ', format(saved, '10d')
print 'total nodes = ', format(name-saved, '10d')
print '  src nodes = ', format(srcnodes,'10d')
print '  lib nodes = ', format(trouble,'10d')

if srcnodes < 20000:
	cmd = "dot -Tsvg "+sys.argv[1].replace('.out','.graph')+' > '+sys.argv[1].replace('.out','.svg')
	os.system(cmd)