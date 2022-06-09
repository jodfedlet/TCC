

#https://github.com/JustAnotherArchivist/snscrape


import pandas as pd
import snscrape.modules.twitter as twitterScraper

query=('haiti OR haitiano OR haitiana lang:pt since:2018-01-01 until:2022-05-31 -filter:replies')

scraper = twitterScraper.TwitterSearchScraper(query)

list_of_teets = []
for idx, tweet in enumerate(scraper.get_items()):
  tweet_dict = {'datetime':tweet.date,'tweet_id':tweet.id,'user_id':tweet.user.id,'text':tweet.content}
  list_of_teets.append(tweet_dict)

df = pd.DataFrame(list_of_teets)
print(len(df))
df.to_csv('csv/all_tweets_without_retweets.csv')
