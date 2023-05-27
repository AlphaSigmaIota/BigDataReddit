# use praw library to access Reddit API
import praw
from praw.models import MoreComments

import pandas as pd

# set access id and secret to reddit app
reddit = praw.Reddit(
    client_id='QK6TtiVAAfZ5XVp3lNHQLw',
    client_secret='Z9fjb3B87YDkZHi8TXtBC4GipN6bcw',
    user_agent='akad_bigdata',
    redirect_uri='http://www.example.com/unused/redirect/uri'
)

# keyword to search for
keyword = "python"
# choose subreddit ('all' for all subreddits)
subreddit = reddit.subreddit('all')

# get posts
posts = subreddit.search(keyword, sort='top', time_filter='all', limit=10)

data = []

for post in posts:
    # extract data from posts
    post_dict = {
        'Titel': post.title,
        #'Inhalt': post.selftext,
        'Autor': post.author.name,
        'Subreddit': post.subreddit.display_name,
        'Anzahl der Kommentare': post.num_comments,
        'Punktzahl': post.score
    }

    # extract comments
    comments = post.comments.list()
    comment_texts = []
    for comment in comments:
        if not isinstance(comment, MoreComments):
            comment_texts.append(comment.body)

    data.append(post_dict)

# create dataframes and save them as csv-files
df_data = pd.DataFrame(data)
df_data.to_csv('Data.csv',sep=';',encoding='utf-8', index=False)

df_comments = pd.DataFrame(comment_texts)
df_comments.to_csv('Comments.csv',sep=';',encoding='utf-8', index=False)