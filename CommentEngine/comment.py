import sys, os, subprocess


functions = sys.argv[1]
location = sys.argv[2]
output = functions.replace('.func','.comments')


namemap = {}
def translate(file, func):
	global namemap

	if not file in namemap:
		namemap[file]={}

		if os.path.isfile(file):
			cmd1 = "objdump -d "+file+" > /tmp/ca.dump"
			cmd2 = "objdump -d -C "+file+" > /tmp/cb.dump"

			# print cmd1
			os.system(cmd1)
			os.system(cmd2)
			
			f1 = open("/tmp/ca.dump",'r')
			f2 = open("/tmp/cb.dump",'r')

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

def cscope(key):
    process = subprocess.Popen(['cscope','-d','cscope.out','-R','-L1',key], stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout

f = open(functions,'r')
func= []
file=''
search=False
for line in f:
	if (line[0]=='@'):
		l = line.split()
		file = l[1]
		if len(l)>1:
			if (l[1][:4]=='/lib') or (l[1][:4]=='/usr'):
				search=False
			else:
				search=True	

	elif search:
		l = line.strip().split()
		
		name = l[3]
		tname = translate(file,name)

		# if not tname==name:
		# 	print "'"+name+"' '"+tname+"'"

		if not tname=='':
			if '::' in tname:
				tname=tname.split('::')[1]
			
			tname=tname.split('(')[0]
			func.append(tname)
f.close()

print sys.argv[1],len(func)

f2 = open(output,'w')
os.chdir(location)

fld = {}
fcd = {}
totalFunc = len(func)
totalFuncComment = 0
totalFuncFound = 0

for fu in func:
	files = cscope(fu).split('\n')
	fldfu=[]
	for fi in files:
		fi = fi.strip().split()
		if len(fi)>=2:
			fldfu.append((fi[0],fi[2])) 
	fld[fu] = fldfu
	if len(fldfu)>0:
		totalFuncFound+=1
	
	cmm = []
	for (fname,lno) in fldfu:
		f1 = open(fname, 'r')
		lines = []
		for i in range(int(lno)-1):
			lines.append(f1.readline())
		lines.reverse()	

		leng = len(lines)
		i = 0
		found = False
		while i<leng:
			if '/*' in lines[i]:
				found = True
				break
			i+=1

		discard = False	
		if found:
			for j in range(i+1):
				if '{' in lines[j] or '}' in lines[j] or '#include' in lines[j]	or '#define' in lines[j]: 
					discard=True
					break
				if '#ifdef' in lines[j] or '#else' in lines[j] or '#endif' in lines[j]:
					discard=True
					break

			if not discard:
				comm = lines[:(i+1)]
				comm.reverse()
				cmm.append((''.join(comm)).replace('\n',' '))
	
	fcd[fu] = cmm
	if len(cmm) >= 1:
		totalFuncComment+=1

f2.write("totalFunctions:"+str(totalFunc)+" totalFuncComment:"+str(totalFuncComment)+" totalFuncFound:"+str(totalFuncFound)+'\n')
for fu in func:
	cmm = fcd[fu]
	if len(cmm)>=1:
		totalFuncComment+=1
		f2.write(fu+' #cmm:'+str(len(cmm))+' #$# ')
		# for i in range(len(cmm)):
		for i in range(1):
			cmm[i] = cmm[i].replace('/*','').replace('*/','').replace('*','').replace('"','').replace('	',' ').replace('\\','').replace('%','').replace('  ','').strip()
			f2.write(cmm[i]+'\n')
	else:
		f2.write(fu+' #cmm:0\n')
