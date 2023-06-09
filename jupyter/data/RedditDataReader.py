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

# choose subreddit ('all' for all subreddits)
subreddit = reddit.subreddit('all')

# get posts
processed_ids = []
processed = False

while True:
    posts = list(subreddit.new())

    for submission in posts:
        if submission.id not in processed_ids:
            print(submission.title)
            post_dict = {
                'Titel': submission.title,
                'Erstellt_UTC': submission.created_utc,
                'Erstellt': datetime.datetime.fromtimestamp(submission.created_utc).isoformat(),
                'Subreddit': submission.subreddit.display_name,
                'Inhalt': submission.selftext
            }
            processed_ids.append(submission.id)
            processed = True
        else:
            processed = False

        byte_like = json.dumps(post_dict).encode('utf-8')
        p.produce('reddit_messages', byte_like)

    #only flush if new posts were submitted
    if processed:
        p.flush()


