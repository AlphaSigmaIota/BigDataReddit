# Autor: HS

# use praw library to access Reddit API
import praw
import datetime
import json
from confluent_kafka import Producer
import time

p = Producer({'bootstrap.servers': 'kafka-broker:9092'})

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
          'time_filter': "year"}
while True:
    posts = list(subreddit.search('*', params=params))
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

    if len(posts) != 0:
        params['after'] = posts[-1].fullname
        p.flush()

    time.sleep(15)

