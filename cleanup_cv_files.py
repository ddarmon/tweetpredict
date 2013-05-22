import os

os.system('cd /Users/daviddarmon/Documents/Reference/R/Research/2013/network/tweetpredict/timeseries_alldays')
os.system('find . -name "*-train-*.*" | xargs /bin/rm')
os.system('find . -name "*-tune-*.*" | xargs /bin/rm')