import os
import tweepy
from collections import defaultdict
from toolz.dicttoolz import valfilter
import random

from collections import namedtuple
Tweet = namedtuple('Tweet', ['screen_name', 'tweet_id'])

CONSUMER_KEY = os.environ['TWITTER_API_KEY']
CONSUMER_SECRET = os.environ['TWITTER_API_SECRET']
ACCESS_KEY = os.environ['TWITTER_ACCESS_TOKEN']
ACCESS_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

SF_WOEID=2487956

CONTACTED_SCREEN_NAMES = set()

def update_status(tweets):
    text = update_status_text(tweets)
    api = twitter_api()
    api.update_status(text, in_reply_to_status_id=tweets[0].tweet_id)
    api.update_status(text, in_reply_to_status_id=tweets[1].tweet_id)


def update_status_text(tweets):
    CONTACTED_SCREEN_NAMES.add(tweets[0].screen_name)
    CONTACTED_SCREEN_NAMES.add(tweets[1].screen_name)

    assert len(tweets) == 2
    comment = 'You said the exact same thing at the exact same time!'
    return '.@{screen_name1} @{screen_name2} {comment}'.format(
        screen_name1=tweets[0].screen_name,
        screen_name2=tweets[1].screen_name,
        comment=comment)


def dig_for_twins(tweets):
    text_to_users = defaultdict(list)
    for tweet in tweets:
        if not tweet.text.startswith('RT') and tweet.user.screen_name not in CONTACTED_SCREEN_NAMES:
            text_to_users[tweet.text].append(Tweet(tweet.user.screen_name, tweet.id))

    twins = valfilter(lambda v: len(v) > 1, text_to_users)

    if len(twins) == 0:
        tweets = None
    else:
        text = random.choice(list(twins.keys()))
        tweets = random.sample(twins[text], 2)

    return tweets


def fetch_tweets(query, fetch_size=10000):
    assert fetch_size > 0
    api = twitter_api()
    tweets = []
    for i, tweet in enumerate(tweepy.Cursor(api.search,
                               q=query,
                               count=100,
                               result_type="recent",
                               include_entities=True,
                               lang="en").items()):
        tweets.append(tweet)
        if i == fetch_size - 1:
            break
    return tweets


def random_trend_query():
    api = twitter_api()
    sf_trends = api.trends_place(SF_WOEID)
    trend_queries = [trend['query'] for trend in sf_trends[0]['trends']]
    return random.choice(trend_queries)


def twitter_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    return tweepy.API(auth)