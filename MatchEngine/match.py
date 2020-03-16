import spacy
import re
import sys

print("1) GET FUNCTIONS")
FUNC = []
NID = []
FN0 = []

fname = [sys.argv[3],sys.argv[4]]

for i in range(2):
	FN0.append([])
	functions = sys.argv[i+1]
	f = open(functions,'r')
	func = {}
	nodeid = {}

	for line in f:
		l = line.strip().split()
		count = int(l[2][2:])
		nid = int(l[0][2:])
		mcount = int(l[3][2:])
		ccount = int(l[4][2:])

		name = ''
		l3 = line.strip().split('D:')[1].split('H:')[0].strip()
		if fname[i] in l3:
			li = l3.split('#')
			if len(li)==2:
				name = li[1]
		else:
			l4 = line.strip().split('H:')[1]
			li = l4.split('$')
			for lii in li:
				if fname[i] in lii:
					name = lii.split('#')[1]
					break

		ni = name.split('(')[0].replace('::',' ')
		name = ni
		name = name.lstrip('_')

		if not name=='':
			if not name in func:
				func[name]=0
				FN0[i].append(name)
			func[name] += count
			nodeid[name] = (nid,mcount,ccount)
			
	f.close()

	print(len(func))

	# for fn in func:
	# 	print(fn)

	FUNC.append(func)
	NID.append(nodeid)

print("3) NLP SCORE")

nlp = spacy.load('en_core_web_md')

FN = []
for i in range(2):
	FN.append([])
	for j in range(len(FN0[i])):
		fname = FN0[i][j]
		val = FUNC[i][fname]
		(nid,mcount,ccount) = NID[i][fname]
			
		name1 = fname[0].upper()+fname[1:]
		name2 = name1.replace('_',' ')
		name = ' '.join(re.findall('[A-Z][^A-Z]*',name2))

		# print(j,'##'+fname+'$$'+name+'$$')

		name = nlp(name)

		cmm=''
		# if fname in CMM[i]:
		# 	cmm = CMM[i][fname]
		FN[i].append((name,cmm,val,fname,nid,mcount,ccount))	


N = len(FN[0])
M = len(FN[1])

print("N:"+str(N))
print("M:"+str(M))

WM = [[0 for j in range(M)] for i in range(N)]

def simi(a,b):
	return a.similarity(b)

for	i in range(N):
	for j in range(M):
		# print(i,j)
		WM[i][j] = -round(simi(FN[0][i][0],FN[1][j][0]),2)

print("4) HUNGARIAN")

from munkres import Munkres

m = Munkres()
indexes = m.compute(WM)

selindexes = []

total = 0
match = []
for row, col in indexes:
    value = WM[row][col]
    total += value
    if -value>=0.6:
    	v1 = FN[0][row][2]
    	v2 = FN[1][col][2]
    	diff = abs(v1-v2)
    	
    	d1 = format(FN[0][row][4],'10d')+' '+format(FN[0][row][3],'50s')+' '+format(v1,'10d')+' '+format(FN[0][row][5],'10d')+' '+format(FN[0][row][6],'10d')
    	d2 = format(FN[1][col][4],'10d')+' '+format(FN[1][col][3],'50s')+' '+format(v2,'10d')+' '+format(FN[1][col][5],'10d')+' '+format(FN[1][col][6],'10d')
    	match.append((d1,d2,-value,diff))
    	selindexes.append((row,col))

print(f'Total cost: {round(total,2)}')

match.sort(key=lambda x:x[3], reverse=True)

print("5) MATCHED")

print('Ins diff'.rjust(15)+'  NLP | '+'Func id'.rjust(10)+' '+format('Function name','50s')+' '+'Ins count'.rjust(10)+' '+'Node ins'.rjust(10)+' '+'Num calls'.rjust(10)+' | '+'Func id'.rjust(10)+' '+format('Function name','50s')+' '+'Ins count'.rjust(10)+' '+'Node ins'.rjust(10)+' '+'Num calls'.rjust(10))

for (a,b,v,d) in match:
	print(format(d,'15d'),format(v,'.2f'),'|',a,'|',b)

print("6) NOT MATCHED")

print('Func ID'.rjust(10)+' '+format('Function Name','50s')+' '+'Ins count'.rjust(10)+' '+'Mcount'.rjust(10)+' '+'Num calls'.rjust(10))

for i in range(2):
	print('FN '+str(i)) 
	matched = [selindexes[j][i] for j in range(len(selindexes))]
	for k in range(len(FN[i])):
		if not k in matched:
			# name,cmm,val,fname,nid,mcount,ccount
			print(format(FN[i][k][4],'10d'),format(FN[i][k][3],'50s'),format(FN[i][k][2],'10d'),format(FN[i][k][5],'10d'),format(FN[i][k][6],'10d'))




