import tweepy

consumer_key = "rUvpe3Rb07ZcH9SPYeeUQA"
consumer_secret = "my2L4jzt6yzckbUtrmFPoA8wan2dzZUdh9zmMAarMhs"

access_token="18088249-RacAIHayGnKcfbks7zlnLJXZERHXpgJmt9bqoi5OI"
access_token_secret="4XdTv4iDp0z7DvgSbw0UF7Sp6PAR3UWhcUfVLdM7Hc"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# If the authentication was successful, you should
# see the name of the account print out
# print api.me().name

# friends = api.lookup_friendships(user_ids = [14777850])
friends = api.lookup_friendships(screen_names = ['lmendy7'])