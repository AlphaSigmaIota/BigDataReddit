# use praw library to access Reddit API
import praw
import datetime
import json
from confluent_kafka import Producer
from praw.models import MoreComments
import time
import pandas as pd

p = Producer({'bootstrap.servers': 'localhost:9092'})

# set access id and secret to reddit app
reddit = praw.Reddit(
    client_id='QK6TtiVAAfZ5XVp3lNHQLw',
    client_secret='Z9fjb3B87YDkZHi8TXtBC4GipN6bcw',
    user_agent='akad_bigdata',
    redirect_uri='http://www.example.com/unused/redirect/uri'
)

# keyword to search for
keyword = "*"
# choose subreddit ('all' for all subreddits)
subreddit = reddit.subreddit('all')

data = []

# get posts
params = {'limit': 100,
          'sort': "new",
          'time_filter': "hour"}
while True:
    posts = list(subreddit.search('*', params=params))
    if not posts:
       break
    for submission in posts:
        print(submission.title)
        post_dict = {
            'Titel': submission.title,
            'Erstellt_UTC': submission.created_utc,
            'Erstellt': datetime.datetime.fromtimestamp(submission.created_utc).isoformat(),
            'Inhalt': submission.selftext
        }

        byte_like = json.dumps(post_dict).encode('utf-8')
        p.produce('reddit_messages', byte_like)

    params['after'] = posts[-1].fullname
    p.flush()

    time.sleep(15)

