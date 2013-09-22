import tweepy

consumer_key = "rUvpe3Rb07ZcH9SPYeeUQA"
consumer_secret = "my2L4jzt6yzckbUtrmFPoA8wan2dzZUdh9zmMAarMhs"

access_token="18088249-RacAIHayGnKcfbks7zlnLJXZERHXpgJmt9bqoi5OI"
access_token_secret="4XdTv4iDp0z7DvgSbw0UF7Sp6PAR3UWhcUfVLdM7Hc"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# friends = api.lookup_friendships(user_ids = [14777850])

user = api.get_user('j_tsar')

timeline_full = []

for page in range(0, 150):
	timeline_full.extend(api.user_timeline(id = user.id, page = page, include_rts = True))

import codecs

wfile = codecs.open('lmendy.txt', encoding='utf-8', mode='w')

for ind in range(1, len(timeline_full) + 1):
	tweet = timeline_full[-ind]

	print tweet.text
	print tweet.created_at

	wfile.write(u'{}\t{}\n'.format(tweet.created_at, tweet.text))

wfile.close()