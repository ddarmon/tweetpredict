import glob

fileList = glob.glob('timeseries_alldays/byday-600s-*.dat')

good_count = 0

for fname in fileList:
	if 'train' in fname or 'tune' in fname or 'test' in fname:
		pass
	else:
		ofile = open(fname)

		line_count = 0

		for line in ofile:
			line_count += 1

		ofile.close()

		print fname, line_count

		if line_count == 49:
			good_count += 1

print good_count
