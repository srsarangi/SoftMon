import sys, os

functions = sys.argv[1]
print functions

output = functions.replace('.fn','.fn1')

namemap = {}
def translate(file, func):
	global namemap

	if not file in namemap:
		namemap[file]={}

		if os.path.isfile(file):
			cmd1 = "objdump -d "+file+" > /tmp/ta.dump"
			cmd2 = "objdump -d -C "+file+" > /tmp/tb.dump"

			# print cmd1
			os.system(cmd1)
			os.system(cmd2)
			
			f1 = open("/tmp/ta.dump",'r')
			f2 = open("/tmp/tb.dump",'r')

			for l1 in f1:
				l2 = f2.readline()

				if ">:" in l1:
					name1 = l1.split('<')[1].split('>')[0]
					name2 = l2.split('<')[1].split('>')[0]

					namemap[file][name1]=name2

	if func in namemap[file]:
		return namemap[file][func]
	else:
		return ''

f = open(functions,'r')
f1 = open(output,'w')

fname = sys.argv[2]

for line in f:
	l = line.strip().split()

	l3=l[5]
	if fname in l[5]:
		ni = l[5].split('#')
		if len(ni)==2:
			tni = translate(ni[0][2:],ni[1])
			if not tni=='':
				l3 = ni[0]+'#'+tni

	l4=[]
	for fni in l[6][2:].split('$'):
		if fname in fni:
			ni = fni.split('#')
			if len(ni)>1:
				tni = translate(ni[0],ni[1])
				if not tni=='':
					l4.append(ni[0]+'#'+tni)
				else:
					l4.append(fni)
			else:
				l4.append(fni)
		else:
			l4.append(fni)

	l4 = '$'.join(l4)

	f1.write(l[0]+' '+l[1]+' '+l[2]+' '+l[3]+' '+l[4]+' '+l3+' H:'+l4+'\n')

f.close()
f1.close()