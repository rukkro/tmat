try:
    from twitter import tweet_filter
    import config, tweepy
    from tweepy import api
    from tweepy import OAuthHandler
except ImportError as e:
    print("Error:", e)
    quit()

auth = OAuthHandler(config.ckey, config.csecret)
auth.set_access_token(config.atoken, config.asecret)
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

def scrape(Setup):
    #http://stackoverflow.com/a/23996991
    searched_tweets = []
    last_id = -1
    successful = 0
    while successful < Setup.lim:
        count = Setup.lim - successful
        try:
            new_tweets = api.search(q=Setup.term,result_type=Setup.result_type,until=Setup.before, count=count, max_id=str(last_id - 1))
            if not new_tweets:
                break
            searched_tweets.extend(new_tweets)
            last_id = new_tweets[-1].id
            for iter, data in enumerate(searched_tweets):
                if tweet_filter.social_filter(data._json):
                    if tweet_filter.duplicate_find(Setup.tweet_coll, data._json):  # if no duplicates found, add tweet to db
                        if Setup.after is None or tweet_filter.date_filter(data._json,Setup.after):
                            Setup.tweet_coll.insert_one(data._json)
                            successful+=1
            searched_tweets[:] = []
            print("\rTweets:", successful,
                  "[{0:50s}] {1:.1f}% ".format('#' * int((successful / int(Setup.lim)) * 50),
                                               (successful / int(Setup.lim)) * 100), end='',flush=True)
        except tweepy.TweepError as e:
            print("Error:",e.args[0])
            return
        except Exception as e:
            print("Error:",e)
