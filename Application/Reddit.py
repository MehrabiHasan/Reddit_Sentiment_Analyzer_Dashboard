### TODO: Filter Out Automated Message From R/Conservative
### Todo: Optimize to work for 1000 Hot Submissions Each.
from config import PRAW_AGENT, PRAW_ID, PRAW_PASS, PRAW_SECRET, PRAW_USER

import datetime
import praw
from praw.models import MoreComments
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import string
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import numpy as np
import pandas as pd
import re

stop_words = set(stopwords.words("english"))

reddit = praw.Reddit(client_id=PRAW_ID,
                     client_secret=PRAW_SECRET,
                     user_agent=PRAW_AGENT,
                     username=PRAW_USER,
                     password=PRAW_PASS)

def std(x):
    return np.std(x)

def var(x):
    return np.std(x)**2

def Clean_Comments(Sentence):
    word_list = []
    punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''
    Sentence = Sentence.lower()
    Sentence = word_tokenize(Sentence)
    for words in Sentence:
        if words not in punc and words not in stop_words:
            word_list.append(words)
    Sentence[:] = [' '.join(word_list[:])]
    Sentiment = sentiment_analysis(Sentence)
    return Sentiment


def sentiment_analysis(sentence):
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dictionary = sid_obj.polarity_scores(sentence)
    return sentiment_dictionary['compound']


### TODO: CLEAN THE COMMENTS
def Calculate_Sentiment(Comments):
    temp_list = []
    for comment in Comments:
        temp_list.append(Clean_Comments(comment))
    return temp_list


def Make_DF (Dictionary, Dataframe):
    df = pd.DataFrame(columns = ['Title','Url','Date','ID','Comments','Sentiment Mean','Sentiment Var','Sentiment Std','Sentiment Type'])
    df['Title'] = Dictionary['title']
    df['Url'] = Dictionary['Url']
    df['Date'] = Dictionary['Date']
    df['ID'] = Dictionary['Post_ID']
    merged = pd.merge(left=Dataframe, right=df, left_on="ID", right_on='ID')
    merged = merged.iloc[:, :-5]
    return merged

subreddit_list = ['Liberal', 'Conservative']

Lib_Post = {"title": [],
            "Url": [],
            "Post_ID": [],
            "Date": [],
            "Comments": [],
            "Sentiment Mean": [],
            "Sentiment Std": [],
            "Sentiment Var": [],
            "Sentiment Type": []}

Lib_Comments = pd.DataFrame(columns= ['Title','Url','ID','Comments','Sentiment','Type'])

Cons_Post = {"title": [],
             "Url": [],
             "Post_ID": [],
             "Date": [],
             "Comments": [],
             "Sentiment Mean": [],
             "Sentiment Std": [],
             "Sentiment Var": [],
             "Sentiment Type": []}

Cons_Comments = pd.DataFrame(columns= ['Title','Url','ID','Comments','Sentiment','Type'])

sub = reddit.subreddit('Liberal')
hot_python = sub.hot(limit = 2000)
for submission in hot_python:
    if not submission.stickied:
        comment_list = []
        Lib_Post['title'].append(submission.title)
        Lib_Post['Url'].append("reddit.com" + submission.permalink)
        Lib_Post['Post_ID'].append(submission.id)
        time = submission.created_utc
        Lib_Post['Date'].append(datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d'))
        for top_level_comment in submission.comments:
            if isinstance(top_level_comment,MoreComments):
                continue
            comment_list.append(top_level_comment.body)
            Lib_Comments = Lib_Comments.append({'Title': submission.title,'Url':"reddit.com" + submission.permalink,'ID':submission.id,'Comments': top_level_comment.body}, ignore_index=True)
        Lib_Post['Comments'].append(comment_list)
print('Got Lib Post')
t2 = '[removed]'
t3 = '[deleted]'
temp = Lib_Comments['Comments']
temp = [sub.replace(t2,'') for sub in temp]
temp = [sub.replace(t3,'') for sub in temp]
Lib_Comments['Comments'] = temp
Lib_Comments['Sentiment'] = Calculate_Sentiment(Lib_Comments['Comments'])


by_temp = Lib_Comments.groupby("Title")['Sentiment'].agg(['mean',std,var])
Lib_Comments_Temp = Lib_Comments.copy(deep=True)
Lib_Comments_Temp = Lib_Comments_Temp.groupby(["ID"])['Comments'].apply('***'.join).to_frame().reset_index()

for (m, s, v) in zip(by_temp['mean'], by_temp['std'], by_temp['var']):
    Lib_Post['Sentiment Mean'].append(m)
    Lib_Post['Sentiment Std'].append(s)
    Lib_Post['Sentiment Var'].append(v)
    if m > 0.05:
        Lib_Post['Sentiment Type'].append('Positive')
    elif m < -0.05:
        Lib_Post['Sentiment Type'].append('Negative')
    else:
        Lib_Post['Sentiment Type'].append('Neutral')
Lib_Comments_Temp['Sentiment Mean'] = list(Lib_Post['Sentiment Mean'])
Lib_Comments_Temp['Sentiment Var'] = list(Lib_Post['Sentiment Var'])
Lib_Comments_Temp['Sentiment Std'] = list(Lib_Post['Sentiment Std'])
Lib_Comments_Temp['Sentiment Type'] = list(Lib_Post['Sentiment Type'])
print('Cleaned Lib Post')
print('Started Conservative Post')
sub = reddit.subreddit('Conservative')
hot_python = sub.hot(limit = 2000)
for submission in hot_python:
    if not submission.stickied:
        comment_list = []
        Cons_Post['title'].append(submission.title)
        Cons_Post['Url'].append("reddit.com" + submission.permalink)
        Cons_Post['Post_ID'].append(submission.id)
        time = submission.created_utc
        Cons_Post['Date'].append(datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d'))
        for top_level_comment in submission.comments:
            if isinstance(top_level_comment,MoreComments):
                continue
            comment_list.append(top_level_comment.body)
            Cons_Comments = Cons_Comments.append({'Title': submission.title,'Url':"reddit.com" + submission.permalink,'ID':submission.id,'Comments': top_level_comment.body}, ignore_index=True)
        t1 = "Tired of reporting this thread? Debate us on discord instead: https://discord.gg/conservative - This is an automated message that appears when probable report abuse is detected. We've found this can lead to a productive discussion in an environment better suited for that sort of thing.\n\n*I am a bot, and this action was performed automatically. Please [contact the moderators of this subreddit](/message/compose/?to=/r/Conservative) if you have any questions or concerns.*"
        t2 = '[removed]'
        t3 = '[deleted]'
        t4 = [sub.replace(t1,'') for sub in comment_list]
        t5 = [sub.replace(t2,'') for sub in t4]
        t6 = [sub.replace(t3,'') for sub in t5]
        t6 = list(filter(None, t6))

        Cons_Post['Comments'].append(t6)
t1 = "Tired of reporting this thread? Debate us on discord instead: https://discord.gg/conservative - This is an automated message that appears when probable report abuse is detected. We've found this can lead to a productive discussion in an environment better suited for that sort of thing.\n\n*I am a bot, and this action was performed automatically. Please [contact the moderators of this subreddit](/message/compose/?to=/r/Conservative) if you have any questions or concerns.*"
t2 = '[removed]'
t3 = '[deleted]'
temp = Cons_Comments['Comments']
temp = [sub.replace(t1,'') for sub in temp]
temp = [sub.replace(t2,'') for sub in temp]
temp = [sub.replace(t3,'') for sub in temp]
Cons_Comments['Comments'] = temp
Cons_Comments['Sentiment'] = Calculate_Sentiment(Cons_Comments['Comments'])


Cons_Comments_Temp = Cons_Comments.copy(deep=True)
Cons_Comments_Temp = Cons_Comments_Temp.groupby(["ID"])['Comments'].apply('***'.join).to_frame().reset_index()
by_temp = Cons_Comments.groupby("ID")['Sentiment'].agg(['mean','var','std'])


for (m, s, v) in zip(by_temp['mean'], by_temp['std'], by_temp['var']):
    Cons_Post['Sentiment Mean'].append(m)
    Cons_Post['Sentiment Std'].append(s)
    Cons_Post['Sentiment Var'].append(v)
    if m > 0.05:
        Cons_Post['Sentiment Type'].append('Positive')
    elif m < -0.05:
        Cons_Post['Sentiment Type'].append('Negative')
    else:
        Cons_Post['Sentiment Type'].append('Neutral')

Cons_Comments_Temp['Sentiment Mean'] = list(Cons_Post['Sentiment Mean'])
Cons_Comments_Temp['Sentiment Var'] = list(Cons_Post['Sentiment Var'])
Cons_Comments_Temp['Sentiment Std'] = list(Cons_Post['Sentiment Std'])
Cons_Comments_Temp['Sentiment Type'] = list(Cons_Post['Sentiment Type'])
print('Cleaned_Conservative Post')

Cons_DF = Make_DF(Cons_Post,Cons_Comments_Temp)
Lib_DF = Make_DF(Lib_Post,Lib_Comments_Temp)
def clean_Sentence(Sentence):
    word_list = []
    punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''
    Sentence = Sentence.lower()
    Sentence = word_tokenize(Sentence)
    for words in Sentence:
        if words not in punc and words not in stop_words:
            word_list.append(words)
    Sentence[:] = [' '.join(word_list[:])]
    return Sentence
Cons_title_clean = [clean_Sentence(i) for i in list(Cons_DF['Title'])]
Cons_title_clean = [j for sub in Cons_title_clean for j in sub]
Cons_DF['Cleaned Title'] = Cons_title_clean
Lib_title_clean = [clean_Sentence(i) for i in list(Lib_DF['Title'])]
Lib_title_clean = [j for sub in Lib_title_clean for j in sub]
Lib_DF['Cleaned Title'] = Lib_title_clean

# #### Figure out the comments and sentiment for president and vp elects
# Lib_Coms = []
# Cons_Coms = []
# for i in Lib_DF['Comments_x']:
#     for y in i.split('***'):
#         Lib_Coms.append(y.lower())
# for i in Cons_DF['Comments_x']:
#     for y in i.split('***'):
#         Cons_Coms.append(y.lower())
#
# T_Lib = list(filter(lambda x: "trump"  in x, Lib_Coms))
# B_Lib = list(filter(lambda x: "biden"  in x, Lib_Coms))
# K_Lib = list(filter(lambda x: "kamala"  in x, Lib_Coms))
# P_Lib = list(filter(lambda x: "pence"  in x, Lib_Coms))
# print(len(T_Lib),len(B_Lib),len(K_Lib),len(P_Lib))
# T_LSent = Calculate_Sentiment(T_Lib)
# B_LSent = Calculate_Sentiment(B_Lib)
# K_LSent = Calculate_Sentiment(K_Lib)
# P_LSent = Calculate_Sentiment(P_Lib)
# print(len(T_LSent),len(B_LSent),len(K_LSent),len(P_LSent))
#
# T_Cons = list(filter(lambda x: "trump"  in x, Cons_Coms))
# B_Cons = list(filter(lambda x: "biden"  in x, Cons_Coms))
# K_Cons = list(filter(lambda x: "kamala"  in x, Cons_Coms))
# P_Cons = list(filter(lambda x: "pence"  in x, Cons_Coms))
# print(len(T_Cons),len(B_Cons),len(K_Cons),len(P_Cons))
# T_CSent = Calculate_Sentiment(T_Cons)
# B_CSent = Calculate_Sentiment(B_Cons)
# K_CSent = Calculate_Sentiment(K_Cons)
# P_CSent = Calculate_Sentiment(P_Cons)
# print(len(T_CSent),len(B_CSent),len(K_CSent),len(P_CSent))
# # dictionary of lists
# t_dict= {'Comment': T_Lib, 'Sentiment': T_LSent}
# t_cdict= {'Comment': T_Cons, 'Sentiment': T_CSent}
# B_dict= {'Comment': B_Lib, 'Sentiment': B_LSent}
# B_cdict= {'Comment': B_Cons, 'Sentiment': B_CSent}
# K_dict= {'Comment': K_Lib, 'Sentiment': K_LSent}
# K_cdict= {'Comment': K_Cons, 'Sentiment': K_CSent}
# P_dict= {'Comment': P_Lib, 'Sentiment': P_LSent}
# P_cdict= {'Comment': P_Cons, 'Sentiment': P_CSent}
#
# T_L = pd.DataFrame(t_dict)
# T_C = pd.DataFrame(t_cdict)
# B_L = pd.DataFrame(B_dict)
# B_C = pd.DataFrame(B_cdict)
# K_L = pd.DataFrame(K_dict)
# K_C = pd.DataFrame(K_cdict)
# P_L = pd.DataFrame(P_dict)
# P_C = pd.DataFrame(P_cdict)
#
# T_L.to_csv('Trump Liberal.csv')
# T_C.to_csv('Trump Conservative.csv')
# B_L.to_csv('Biden Liberal.csv')
# B_C.to_csv('Biden Conservative.csv')
# K_L.to_csv('Kamala Liberal.csv')
# K_C.to_csv('Kamala Conservative.csv')
# P_L.to_csv('Pence Liberal.csv')
# P_C.to_csv('Pence Conservative.csv')


Lib_DF.to_excel('Liberal_Sentiment_Newer.xlsx')
Cons_DF.to_excel('Conservative_Sentiment_Newer.xlsx')
print(f'Done!')