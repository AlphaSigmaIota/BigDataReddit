# use praw library to access Reddit API
import praw
import datetime
import json
from confluent_kafka import Producer
from praw.models import MoreComments

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
        p.produce('twitter_messages', byte_like)

        # Hier die Kafka Nachricht
        data.append(post_dict)

    params['after'] = posts[-1].fullname
    p.flush()

        #'Autor': submission.author.name,
        #'Subreddit': submission.subreddit.display_name,
        #'Anzahl der Kommentare': submission.num_comments,
        #'Punktzahl': submission.score

    # extract comments
    # comments = post.comments.list()
    # comment_texts = []
    # for comment in comments:
    #     if not isinstance(comment, MoreComments):
    #         comment_texts.append(comment.body)
    data.append(post_dict)

# create dataframes and save them as csv-files
df_data = pd.DataFrame(data)
df_data.to_csv('Data.csv',sep=';',encoding='utf-8', index=False)

# df_comments = pd.DataFrame(comment_texts)
# df_comments.to_csv('Comments.csv',sep=';',encoding='utf-8', index=False)