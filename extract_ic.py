ofile = open('informational-coherence.dat')

wfile = open('ic.dat', 'w')

line_ind = 1

for line in ofile:
	ics = line.split(' ')

	for ind in range(line_ind, 3000):
		wfile.write(ics[ind].rstrip('\n') + '\n')

	line_ind += 1

ofile.close()

wfile.close()