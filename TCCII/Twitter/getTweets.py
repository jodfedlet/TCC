

#https://github.com/JustAnotherArchivist/snscrape/blob/master/README.md


import pandas as pd
import snscrape.modules.twitter as twitterScraper

scraper = twitterScraper.TwitterSearchScraper(('haiti OR haitiano OR haitiana lang:pt since:2018-01-01 until:2022-05-04'))

count = 0
list_of_teets = []
for idx, tweet in enumerate(scraper.get_items()):
  # if tweet.date.year < 2018 or (tweet.date.year == 2022 and tweet.date.month > 5):
  #   break
  tweet_dict = {'datetime':tweet.date,'tweet_id':tweet.id,'user_id':tweet.user.id,'text':tweet.content}
  list_of_teets.append(tweet_dict)
  count = idx
print(count)
#result = 185221

df = pd.DataFrame(list_of_teets)
df.to_csv('all_tweets.csv')
