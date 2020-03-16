import sys


f = open(sys.argv[1],'r')
f.readline()

srcdic = {}
countdic = {}
allfn = {}

for line in f:
	l = line.strip().split()

	if not len(l)==5:
		continue

	if l[4]=="Instructions":
		continue

	if not l[1] in srcdic:
		srcdic[l[1]] = {}
		countdic[l[1]] = 0

	count = int(l[4])
	calls = int(l[3])
	fname = l[0]
	file = l[1]

	ff = file+':'+fname
	if not ff in allfn:
		allfn[ff] = (0,0)
	(cn1,cl1) = allfn[ff]
	allfn[ff] = (cn1+count, cl1+calls)

	if not fname in srcdic[l[1]]:
		srcdic[l[1]][fname] = (0,0)
	(cn1,cl1) = srcdic[l[1]][fname]
	srcdic[l[1]][fname] = (cn1+count, cl1+calls)
	countdic[l[1]] += count

countlist = []
total = 0
for src in countdic:
	countlist.append((src,countdic[src]))
	total+=countdic[src]

countlist.sort(reverse=True, key= lambda x: x[1])

allfnlist = []
for ff in allfn:
	(ct,calls) = allfn[ff]
	allfnlist.append((ff,ct,calls))

allfnlist.sort(reverse=True, key = lambda x: x[1])
f = open(sys.argv[1].replace('-proccount.out','.func1'),'w')
for (ff,ct,calls) in allfnlist:
	[file,fn] = ff.split(':')
	f.write(format(ct,'15d')+' '+format(calls,'7d')+' '+str(round(ct*100.0/total,3)).rjust(6)+'% '+format(file,'70s')+' '+fn+'\n')
f.close()

f = open(sys.argv[1].replace('-proccount.out','.func'),'w')
for (src,count) in countlist:
	f.write('@ '+src+' count:'+str(count)+' '+str(round(count*100.0/total,3))+'%\n')
	fins = []
	for fname in  srcdic[src]:
		(ct,calls) = srcdic[src][fname]
		fins.append((fname,ct,calls))

	fins.sort(reverse=True, key= lambda x: x[1])

	for (fi,ct,calls) in fins:
		f.write(format(ct,'15d')+' '+format(calls,'7d')+' '+str(round(ct*100.0/count,3))+'% '+fi+'\n')

f.close()