# Code to compress the binarized time series files for
# easy of sending via email, etc. Basically, we had to
# filter out the results files and only get down to
# the actual .dat files.
# 
# The 3K users, at 1s time resolution, compress down
# to about 15 MB, compared to 8 GB.

#	DMD, 150713-15-01

import glob

import tarfile

import gzip

tar = tarfile.open('15K_timeseries.tar', 'w')

fnames = glob.glob('timeseries/byday-600s-*.dat')

for fname in fnames:
	if 'train' not in fname and 'states' not in fname and 'test' not in fname:
		tar.add(fname)

tar.close()

f_in = open('15K_timeseries.tar', 'rb')

f_out = gzip.open('15K_timeseries.tar.gz', 'wb')

f_out.writelines(f_in)

f_out.close()

f_in.close()