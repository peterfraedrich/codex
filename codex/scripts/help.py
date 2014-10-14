#!/usr/bin/python

def setup_subnet(subnet):
	range1 = []
	range2 = []
	subnetlist = []
	a = open('range_1','r')
	b = open('range_2', 'r')
	for i in a:
		range1.append(str(i))
	for i in b:
		range2.append(str(i))
	net = subnet.split('/')
	netmask = int(net[1])
	octet = net[0].split('.')
	for i in octet:
		i = int(i)
	if netmask == 24:
		iprange = octet[0]+'.'+octet[1]+'.'+octet[2]+'.'
		for i in range1:
			subnetlist.append(iprange+i)
		a.close()
	if netmask == 16:
		iprange = octet[0]+'.'+octet[1]+'.'
		for x, y in [(x,y) for x in range1 for y in range2]:
			subnetlist.append(iprange + x.strip('\n') + '.' + y.strip('\n'))
	if netmask == 8:
		iprange = octet[0]+'.'
		for x, y, z in [(x,y,z) for x in range1 for y in range1 for z in range2]:
			subnetlist.append(iprange + x.strip('\n') + '.' + y.strip('\n') + '.' + z.strip('\n'))
	if netmask == 0:
		for w, x, y, z in [(w,x,y,z) for w in range1 for x in range1 for y in range1 for z in range2]:
			subnetlist.append(w.strip('\n') + '.' + x.strip('\n') + '.' + y.strip('\n') + '.' + z.strip('\n'))
	return subnetlist

x = setup_subnet('0.0.0.0/0')
print x