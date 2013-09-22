# A script that takes in a uid and returns the username.

# DMD, 020913-10-55

import sys
import os

from itertools import islice

users = sys.argv[2:]
lookup_type = sys.argv[1] # Either 'un' for username or 'ui' for userid

userid_to_username = {}
username_to_userid = {}

with open('user_lookup/tweet_counts_labeled.tsv') as ofile:
	for line in islice(ofile, 1, None): # Skip the first line, which is a header line
		uid, username, count = line.strip().split('\t')

		userid_to_username[uid] = username

		username_to_userid[username] = uid


for user in users:
	if lookup_type == 'un':
		userid = user
		uname = userid_to_username[userid]
	elif lookup_type == 'ui':
		uname = user
		userid = username_to_userid[uname]

	os.system('open http://twitter.com/account/redirect_by_id?id={}'.format(userid))

	print uname, userid