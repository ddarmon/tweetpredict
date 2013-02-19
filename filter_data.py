ofile = open('byday-600s-184274305-train.dat_inf.dot')

CSM = {} # A dictionary structure for the CSM

for i in range(6):
	ofile.readline()

line = ofile.readline()

while line != '}':
	state = int(line.split()[0]) # The state from the .dot file
	up_prob = 1 - float(line.split()[6]) # The probability of transitioning from this state emitting a 1
	CSM[state] = up_prob # populate the CSM
	
	line = ofile.readline()

ofile.close()

###!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
## Start from *here*. 
###!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

CSM[-1] = 0 # If we are unsure about our state, just don't buy

print CSM

states = {} # A dictionary structure with the ordered pair
			# (symbol sequence, state)

# Populate states from CSM_states

ofile2 = open('CSM_states')

for line in ofile2:
	symbol = line.split()[0]
	state  = line.split()[1]
	
	states[symbol] = state

ofile2.close()

# Open the file containing the time series from the 
# to-be-predicted time period

ofile3 = open('DJIA_binary_1950_1969.dat')

tmp = ofile3.readline().split()

ofile3.close()

# Make time_series one giant string that we can loop through

time_series = ''

for symbol in tmp:
	time_series = time_series + symbol

# predicted_time_series contains our guess for what the time
# series will actually look like

predicted_time_series = ''

# Since we can't possibly make any prediction for the first
# three days (given L for our CSM), we mark those as -1
# to indicate our inability to make a prediction

predicted_time_series = predicted_time_series + '-1 -1 -1 '

# We can predict the fourth day, since we know the three previous days

if CSM[int(states[time_series[0:3]])] > 0.5:
	predicted_time_series = predicted_time_series + '1 '
else:
	predicted_time_series = predicted_time_series + '0 '

# From here on out, we have four days worth of information (using what)
# //actually// happened. As such, we can just loop through the
# time-series until the very end.

num_symbols = len(tmp)

for i in range(num_symbols - 4 + 1):
	if CSM[int(states[time_series[i:i+4]])] > 0.5:
		predicted_time_series = predicted_time_series + '1 '
	else:
		predicted_time_series = predicted_time_series + '0 '

predicted_time_series = predicted_time_series.split()

hits = 0
total = 0

for i in range(num_symbols):
	if time_series[i] == predicted_time_series[i]:
		hits = hits + 1
	total = total + 1
	
	print time_series[i], predicted_time_series[i]

print float(hits) / float(total)