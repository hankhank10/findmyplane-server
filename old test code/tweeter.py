import tweepy

# Authenticate to Twitter
auth = tweepy.OAuthHandler("",
    "")
auth.set_access_token("",
    "")


# Create API object
api = tweepy.API(auth)


# Create a tweet
def post_tweet(tweet_content):
    #api.update_status(tweet_content)
    return
