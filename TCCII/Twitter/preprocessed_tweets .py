# -*- coding: utf-8 -*-
"""preprocessing_tweets.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1j7KNbdTNjbe44DsJnimn4jgNigEV9rTH

#Objetivos
- Visualizar os tweets antes e depois do pré-processamento
  - Quantidade de tweets - quantidade de plavras por tweets e média de palavras dos tweets geral/por ano e por mês
- Pre-processar os tweets:
  - remoção de stop words 
  - remoção de URLs
  - conversão dos textos em letras minúsculas
  - remoção de pontuação e acentuação
  - remocação de palavras com menos:
      - que iniciam com os caracteres @ ou #
      - que possuem menos de 3 caracteres que são diferentes de ht ( sigla do país haiti)
      - palavras que possuem mais de 3 occorências seguidas ( ex: kkkkkk)
  - aplicação de bigrams ( técnica que faz com que palavras que aparecem juntas permaneçam juntas. Ex: Rio de Janeiro = rio_janeiro)
  - lematização dos tweets (processo no qual é realizada uma análise morfológica das palavras, por
exemplo palavras da terceira posição são alteradas para a primeira e verbos no passado e
futuro transformados no presente)

###Importando/instalando bibliotecas
"""

!pip install unidecode
!python3 -m spacy download pt_core_news_sm
!pip install gensim

import pandas as pd
import numpy as np
import nltk
import re
import spacy
import gensim
import matplotlib as mpl
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from google.colab import drive
drive.mount("/content/drive")
nltk.download('all-corpora')
nltk.download('punkt')
nltk.download('rslp')

from nltk.corpus import stopwords
from unidecode import unidecode
from nltk.tokenize import word_tokenize
from nltk.tokenize import wordpunct_tokenize
from nltk import regexp_tokenize
from gensim.models import Phrases

"""# Carregamento dos tweets"""

try:
  tweets_orig = pd.read_csv('/content/drive/My Drive/Colab Notebooks/TCC/csv/all_tweets_with_retweets.csv', lineterminator='\n', index_col=0)
  # tweets_orig['date'] = pd.to_datetime(tweets_orig.datetime).dt.strftime("%Y-%m-%d")
  # tweets_orig = tweets_orig.set_index('date')
  # tweets_orig = tweets_orig.drop(columns="datetime")
except Exception as e:
  print(e)

tweets_orig.shape

tweets_orig.head()

"""#Estatística dos tweets"""

def tweets_stats(df, option):
  df['datetime'] = pd.to_datetime(df.datetime, format='%Y-%m-%d')

  def get_df_len__count_words__mean(df):
    count_all_tweets = len(df)

    if option == 'pre':
       df_text = df['text_preprocessed']
    else:
       df_text = df['text']

    df['count_word'] = df_text.str.split().str.len()
    count_all_words = df['count_word'].sum()
    mean = round(count_all_words / count_all_tweets, 2)
    return (df, count_all_tweets, count_all_words, mean)

  #data by year
  def plot_by_year(): 
    by_year = df.groupby([df['datetime'].dt.year.rename('Year')]).agg({'tweet_id':['count'], 'count_word': ['sum']}).reset_index()
    by_year.columns = ['Year', 'Count tweets', 'Count words']
    by_year = by_year.assign(Mean_words = lambda x: round(x['Count words'] / x['Count tweets'], 2))
    print(by_year)

  #data by 3 month
  def quartely(): 
    trimestral = df.groupby(pd.Grouper(key='datetime', freq='3M', closed='left')).agg({'tweet_id':['count'], 'count_word': ['sum']}).reset_index()
    trimestral.columns = ['Date', 'Count tweets', 'Count words']
    trimestral = trimestral.assign(Mean_words = lambda x: round(x['Count words'] / x['Count tweets'], 2))
    print(trimestral)

  #by year month
  def plot_by_year_and_month():
    by_year_month = df.groupby([df['datetime'].dt.year.rename('Year'), df['datetime'].dt.month.rename('Month')]).agg({'tweet_id':['count'], 'count_word': ['sum']}).reset_index()
    by_year_month.columns = ['Year', 'Month', 'Count tweets', 'Count words']
    by_year_month = by_year_month.assign(Mean_words = lambda x: round(x['Count words'] / x['Count tweets'], 2))
    print(by_year_month)
   
  df, df_len, count_words, mean_words  = get_df_len__count_words__mean(df)
  # print('Total: {0}, Count word: {1}, Mean words: {2}'.format(df_len,count_words, mean_words))
  # print()

  print('*****Agrupado por ano****')
  plot_by_year()
  print('\n')
  
  print('*****Agrupamento trimestral****')
  quartely()
  print('\n')

  print('*****Agrupado por mês e ano****')
  plot_by_year_and_month()

"""###Estatística dos tweets antes do pré-processamento:"""

tweets_stats(tweets_orig, 'ori')

"""#Pegar os stop words da língua portuguesa usando NLTK"""

stop_words = set(stopwords.words('portuguese'))

type(stop_words)

stop_words

"""#Pré-processamento dos tweets

###Função para limpar os tweets
"""

def cleaning(tweet):
  
  #remover pontuações
  def remove_punctuation(tweet):
      return re.sub(r'[^\w\s]','',tweet) 

  #remocao de plavras com mais de 3 ocorrencias seguidas
  def mais_de_3_ocorrencias_seguidas(word):  
    let_ant = word[0]
    count = 0
    mais_de_3 = False;
    for w in word:
      count = count + 1 if w == let_ant else 1
      let_ant = w  
      if count > 3: 
        mais_de_3 = True 
        break  
    return mais_de_3   

  #remover acentuações
  def remove_emphasis(token):
        return unidecode(remove_punctuation(token))

  stop_words_list = [remove_emphasis(st_word) for st_word in stop_words]
 
  #conversão de string para minúsculas, remoção de pontuação, palavras que iniciam com @, #, stopwords ou com tamanho < 2 e se forem diferentes de ht.
  def remove_undesirable_words(tweet):
      new_list_ = []
      tweet = ' '.join(str(word).lower() for word in tweet.split() if not word.startswith('@') and not word.startswith('#'))
     
      for token in wordpunct_tokenize(tweet):
         if token in stop_words_list or (len(token) < 3 and token != 'ht') or mais_de_3_ocorrencias_seguidas(token): continue
         new_list_.append(remove_emphasis(token))
      return ' '.join(new_list_)

  #remover urls
  def remove_url(tweet_without_sw):
      return re.sub(r"http\S+", "", tweet_without_sw)

  #remover palavras que contem ou que são números
  def remove_numeric(tweet):
    return re.sub(r'\d+', '', tweet)

  tweet = remove_url(tweet)
  tweet = remove_numeric(tweet)
  tweet = remove_undesirable_words(tweet)
  return tweet

"""
###Exemplo de tweet antes da aplicação da função de limpeza"""

string_example = "No Rio de Janeiro, em 2021, <p> o nao @senhor vai #investir, em 2022, na educação da Venezuela, Argentina, Haiti,cuba.e etc países comunistas?, porque aqui no Brasil o Senhor nunca fez isso ?????. https://t.co/jmVSYbsG2X"

filtered_tweet = cleaning(string_example)

"""###Exemplo de tweet depois da aplicação da função de limpeza"""

filtered_tweet

"""###Aplicação da função de limpeza dos tweets"""

tweets_pre_proc = tweets_orig.copy()
tweets_pre_proc['text_preprocessed'] = tweets_orig['text'].map(lambda tweet: cleaning(tweet))

tweets_orig.text.head().tolist()

tweets_pre_proc.text_preprocessed.head().tolist()

"""###Remover tweets com menos de 3 palavras"""

tweets_pre_proc = tweets_pre_proc.loc[tweets_pre_proc['text_preprocessed'].str.split().str.len() > 3]

tweets_pre_proc.shape

"""###Remover os tweets duplicados"""

tweets_pre_proc.drop_duplicates(subset = ["text_preprocessed"], keep='first', inplace=True)

"""###Quantidade de tweets após a remoção dos tweets duplicados"""

tweets_pre_proc.shape

tweets_orig.text.head().tolist()

tweets_pre_proc.text_preprocessed.head().tolist()

"""###Estatística dos tweets após o pré-processamento:"""

tweets_stats(tweets_pre_proc, 'pre')

"""###Lematização e stemização"""

pln = spacy.load('pt_core_news_sm')

"""###Bigramas"""

def bigrams(df, option):
  data = df.text_lematizados if option =='lem' else df.text_stematizados
  docs = [doc.split() for doc in data]
  bigram = Phrases(docs, min_count=3)
  for i in range(len(docs)):
    docs[i] = ' '.join(bigram[docs[i]])
  return docs

"""###Lematização"""

string_lem_example = 'lixo tiver nada sou capacetes brancos ajudaram haiti pare besteira ajudou haiti fim exercito capacetes brancos resolvem problema presos campos concentracao argentina criou'

def lemmatization(tweet):
  document = pln(tweet)
  return ' '.join([str(token.lemma_).lower() for token in document])

tweet_lem_example = lemmatization(string_lem_example)

tweet_lem_example

tweets_pre_proc['text_lematizados'] = tweets_pre_proc['text_preprocessed'].map(lambda tweet: lemmatization(tweet))

tweets_pre_proc.text_lematizados.head().tolist()

tweets_pre_proc['bigrams_lem'] = bigrams(tweets_pre_proc, 'lem')

tweets_pre_proc.bigrams_lem.head().tolist()

"""###Stematização"""

string_stem_example = 'capacetes brancos ajudaram haiti pare besteira ajudou haiti fim exercito capacetes brancos resolvem problema presos campos concentracao argentina criou'

def stemming(tweet):
  document = pln(tweet)
  stemmer = nltk.stem.RSLPStemmer()
  return ' '.join([str(stemmer.stem(token.text)).lower() for token in document])

string_stem_example = stemming(string_stem_example)

string_stem_example

tweets_pre_proc['text_stematizados'] = tweets_pre_proc['text_preprocessed'].map(lambda tweet: stemming(tweet))

tweets_pre_proc.text_stematizados.head().tolist()

tweets_pre_proc['bigrams_stem'] = bigrams(tweets_pre_proc,'stem')

tweets_pre_proc.bigrams_stem.head().tolist()

"""#Comparação de tweets originais, pré-processados, lematizados, **bigramados e **stematizados

###Tweets originais
"""

tweets_orig.text.head().tolist()

"""### Tweets pré-processados"""

tweets_pre_proc.text_preprocessed.head().tolist()

"""###Tweets lematizados"""

tweets_pre_proc.text_lematizados.head().tolist()

"""###Tweets com bigramas"""

tweets_pre_proc.bigrams_lem.head().tolist()

"""###Tweets stematizados"""

tweets_pre_proc.text_stematizados.head().tolist()

"""##Criando o arquivo .csv dos tweets"""

df = pd.DataFrame(tweets_pre_proc)
df.to_csv('/content/drive/My Drive/Colab Notebooks/TCC/csv/pre_processed_tweets.csv')