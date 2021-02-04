import tweepy

# Authenticate to Twitter
auth = tweepy.OAuthHandler("oVkaUjEmvqGhQcEzh0lVjD8dB",
    "YD1skn8LSA8pGJC1gbHnE9qxg7oT4HCBqCdScTzBh2lktyiWfs")
auth.set_access_token("1356724866670620677-cJGJd6Zj5AuWWjIYeuzhZsSxZUHoxK",
    "1K6EsUKV356Z7M1Rg03SKJrQzDp7wWxXO9K8imqt4F5kg")


# Create API object
api = tweepy.API(auth)


# Create a tweet
def post_tweet(tweet_content):
    #api.update_status(tweet_content)
    return
