import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# df=pd.DataFrame({'x':[100,200,300,400],'y':[56,678,6456,876]})
# app = dash.Dash()
# fig=px.bar(df,x='x',y='y')

import time
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from nltk.stem import WordNetLemmatizer #word stemmer class
lemma = WordNetLemmatizer()
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import pickle
import joblib
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
import nltk
# import re
import string
app = dash.Dash()
app.title = 'Real-Time Twitter Monitor'

server = app.server

pos = 0
neg = 0
time = 0
'''
vectorizer = pickle.load(open("vector.pickel", "rb"))
w = pickle.load(open('train', 'rb'))
x_train=w['x_train']
vectorizer.fit(x_train)
print(vectorizer)
print(len(vectorizer.get_feature_names()))
filename = 'logR.sav'''
tf2=pd.DataFrame(columns=['pos','neg','time'])
# filename='logR.sav'
#loaded_model = joblib.load(open(filename, 'rb'))
# def calctime(a):
#     return time.time() - a
# #
# #
positive = 0
negative = 0
neutral = 0
compound=0
#
# tf={'pos':pos,'neg':neg,'time':time}
# count = 0
# initime = time.time()
#
# tf = pd.DataFrame(columns=['pos','neg','neu',time])
#ps = PorterStemmer()
#wnl = WordNetLemmatizer()
# plt.ion()
# import test
#

# ckey = 'WnyAgUaacX1YheRSJqwMhhZgR'
# csecret = 'LzHg7GuAfJNIsHRpRXEk72TaEjcG5RL9yl85c0rbI1V1pg6rHQ'
# atoken = "1125091796046843905-DNeIxEe9RNwlwzZZXwXEW3VJFlv7Az"
# asecret = "n3Yc9GzA2Saa6LNPZ5465WdQNj06G6hBrqcWnpwkc4jCb"
#
# df=pd.DataFrame({'positive':[positive],'negative':[negative],'neutral':[neutral]})
#
# fig=px.bar(df,x=['positive','negative','neutral'])
#
# # @app.callback([Output('test','children')])
# #               # [Output('trend','fig')],
# #               # [Input('interval-component-slow','n_intervals')])
# # def update_graph():
# #     content='hello world'
#
#
#     # return content
cal={'val':['positive','negative'],'count':[positive,negative]}
cal=pd.DataFrame(cal)
app.layout = html.Div([
    dcc.Graph(id='trend'),
    dcc.Graph(id='trend2'),
    dcc.Interval(
        id='interval-component-slow',
        interval=1 * 9000,  # in milliseconds
        n_intervals=0
    )
], style={'padding': '20px'})


@app.callback(
              [Output('trend2','figure')],
              [Input('interval-component-slow','n_intervals')])
def update_graph(n):
    global positive
    global negative
    content='hi'
    # print(cal)
    try:
        df=pd.read_json('count.json')
        print(df['details'][0]['tweet'])
    except:
        print("cant")
    global pos
    global neg
    global time
    global tf2
    positive=df['pos'][0]

    negative = df['neg'][0]
    cal.loc[cal['val']=='positive','count']=positive
    cal.loc[cal['val']=='negative','count']=negative
    time=df["time"][0]
    temp={'pos':positive,'neg':negative,'time':time,'text':df['details'][0]}
    # print(temp)
    temp=pd.DataFrame(temp,columns=['pos','neg','time','details'],index=[[1]])
    # print(temp)
    tf2=pd.concat([tf2,temp],ignore_index=True)
    tf2.drop_duplicates(subset=['details'],inplace=True)
    print(len(tf2))
    x=list([20,30,204,309])
    y=list([90,345,234,234])
    fig=px.bar(cal,x='val',y='count')
    # fig2=px.scatter(tf,x='time',y=[['pos','neg']],color=[['pos','neg']])
    fig2=px.scatter(tf2,x='time',y=['neg','pos'])




    return [fig2]






if __name__ == '__main__':
    app.run_server(debug=True)




