from cloudant import Cloudant #!!COMMENTED FROM BHUSHAN'S CODE!!
from flask import Flask, render_template, request, jsonify
import atexit #!!COMMENTED FROM BHUSHAN'S CODE!!
import time as tm
import os
import json
import dash
import plotly
import dash_core_components as dcc
import dash_html_components as html
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go #added
import pandas as pd
import plotly.io as pio
import plotly.express as px
import nltk
import regex as re
from plotly.subplots import make_subplots
import json
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer #word stemmer class
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import pickle
import string
import joblib
from nltk.corpus import stopwords

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        apikey= creds['apikey']
        url = 'https://' + creds['host']
        client = Cloudant.iam(user,apikey,url=url, connect=True)
        db = client['live']
elif "CLOUDANT_URL" in os.environ:
    client = Cloudant.iam(os.environ['CLOUDANT_USERNAME'], os.environ['CLOUDANT_PASSWORD'], url=os.environ['CLOUDANT_URL'], connect=True)
    db = client['live']
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['apikey']
        url = 'https://' + creds['host']
        client = Cloudant.iam(user, password, url=url, connect=True)
        db = client['live']
app = dash.Dash(__name__)
old_time='0:0'
old_tweet='23kcbasngjbfj'
lemma = WordNetLemmatizer()




pos = 0
neg = 0
time = 0
vectorizer = pickle.load(open("vector.pickel", "rb"))
w = pickle.load(open('train', 'rb'))
x_train=w['x_train']
vectorizer.fit(x_train)
print(vectorizer)
print(len(vectorizer.get_feature_names()))
filename = 'logR.sav'
tf2=pd.DataFrame(columns=['pos','neg','neu','time','text','label','hashtags'])
loaded_model = joblib.load(open(filename, 'rb'))
positive = 0
negative = 0
neutral = 0
compound=0
ps = PorterStemmer()
wnl = WordNetLemmatizer()
time='as'
cal={'val':['positive','negative','neutral'],'time':[time,time,time],'count':[negative,neutral,positive]}
cal=pd.DataFrame(cal)

df1 = pd.read_csv('Lockdowns/lock1.csv',encoding='latin')
df2 = pd.read_csv('Lockdowns/lock2.csv',encoding='latin')
df3 = pd.read_csv('Lockdowns/lock3.csv',encoding='latin')
df4 = pd.read_csv('Lockdowns/lock4.csv',encoding='latin')

df1[['day','time']]=df1.date.str.split(expand=True)
df1=df1.drop(['date'],axis=1)
df2[['day','time']]=df2.date.str.split(expand=True)
df2=df2.drop(['date'],axis=1)
df3[['day','time']]=df3.date.str.split(expand=True)
df3=df3.drop(['date'],axis=1)
df4[['day','time']]=df4.date.str.split(expand=True)
df4=df4.drop(['date'],axis=1)

dates = pd.DataFrame()
dates2 = pd.DataFrame()
dates3 = pd.DataFrame()
dates4 = pd.DataFrame()
dates = df1[['day','time','labels','text']]
date2 = df2[['day','time','labels','text']]
date3 = df3[['day','time','labels','text']]
date4 = df4[['day','time','labels','text']]
dates = dates.append(date2,ignore_index=True)
dates = dates.append(date3,ignore_index=True)
dates = dates.append(date4,ignore_index=True)

lemma = WordNetLemmatizer()

# Use this for hashtag extract
port = int(os.getenv('PORT', 8900))
def hashtag_extract(x):
    hashtags = []

    # Loop over the words in the tweet
    for i in x:
        ht = re.findall(r"#(\w+)", i)
        ht=[hts.lower() for hts in ht]
        #ht=map(str.lower,ht)


        hashtags.append(ht)
    return hashtags
#-------------------------Lockdown1------------------
HT_regular = hashtag_extract(df1['text'][df1['labels'] == 0])
# extracting hashtags from racist/sexist tweets
HT_negative = hashtag_extract(df1['text'][df1['labels'] == -1])
HT_positive = hashtag_extract(df1['text'][df1['labels'] == 1])
# unnesting list
HT_regular = sum(HT_regular,[])
HT_negative = sum(HT_negative,[])
HT_positive = sum(HT_positive,[])
#print(HT_regular,file=sys.stderr)
#print(HT_negative,file=sys.stderr)
#positive hashtags
a = nltk.FreqDist(HT_regular)
d = pd.DataFrame({'Hashtag': list(a.keys()),
                  'Count': list(a.values())})
# selecting top 10 most frequent hashtags     
d = d.nlargest(columns="Count", n = 5) 
d.head()
#plt.figure(figsize=(22,10))
#ax = sns.barplot(data=d, x= "Hashtag", y = "Count")
#ax.set(ylabel = 'Count')
#plt.show()
#negative hastags funtion will come over here
b = nltk.FreqDist(HT_negative)
e = pd.DataFrame({'Hashtag': list(b.keys()), 'Count': list(b.values())})
# selecting top 10 most frequent hashtags
e = e.nlargest(columns="Count", n = 5)   
#plt.figure(figsize=(16,5))
#ax = sns.barplot(data=e, x= "Hashtag", y = "Count")
#ax.set(ylabel = 'Count')
#plt.show()'''
g = nltk.FreqDist(HT_positive)
h = pd.DataFrame({'Hashtag': list(g.keys()),
                  'Count': list(g.values())})
# selecting top 10 most frequent hashtags     
h = h.nlargest(columns="Count", n = 5) 

#-----------------------Lockdown2----------------------------
HT_regular = hashtag_extract(df2['text'][df2['labels'] == 0])
# extracting hashtags from racist/sexist tweets
HT_negative = hashtag_extract(df2['text'][df2['labels'] == -1])
HT_positive = hashtag_extract(df2['text'][df2['labels'] == 1])
# unnesting list
HT_regular = sum(HT_regular,[])
HT_negative = sum(HT_negative,[])
HT_positive = sum(HT_positive,[])
#print(HT_regular,file=sys.stderr)
#print(HT_negative,file=sys.stderr)
#positive hashtags
a2 = nltk.FreqDist(HT_regular)
d2 = pd.DataFrame({'Hashtag': list(a2.keys()),
                  'Count': list(a2.values())})
# selecting top 10 most frequent hashtags     
d2 = d2.nlargest(columns="Count", n = 5) 
d2.head()
#plt.figure(figsize=(22,10))
#ax = sns.barplot(data=d, x= "Hashtag", y = "Count")
#ax.set(ylabel = 'Count')
#plt.show()
#negative hastags funtion will come over here
b2 = nltk.FreqDist(HT_negative)
e2 = pd.DataFrame({'Hashtag': list(b2.keys()), 'Count': list(b2.values())})
# selecting top 10 most frequent hashtags
e2 = e2.nlargest(columns="Count", n = 5)   
#plt.figure(figsize=(16,5))
#ax = sns.barplot(data=e, x= "Hashtag", y = "Count")
#ax.set(ylabel = 'Count')
#plt.show()'''
g2 = nltk.FreqDist(HT_positive)
h2 = pd.DataFrame({'Hashtag': list(g2.keys()),
                  'Count': list(g2.values())})
# selecting top 10 most frequent hashtags     
h2 = h2.nlargest(columns="Count", n = 5) 

#---------------------Lockdown3---------------------
HT_regular = hashtag_extract(df3['text'][df3['labels'] == 0])
# extracting hashtags from racist/sexist tweets
HT_negative = hashtag_extract(df3['text'][df3['labels'] == -1])
HT_positive = hashtag_extract(df3['text'][df3['labels'] == 1])
# unnesting list
HT_regular = sum(HT_regular,[])
HT_negative = sum(HT_negative,[])
HT_positive = sum(HT_positive,[])
#print(HT_regular,file=sys.stderr)
#print(HT_negative,file=sys.stderr)
#positive hashtags
a3 = nltk.FreqDist(HT_regular)
d3 = pd.DataFrame({'Hashtag': list(a3.keys()),
                  'Count': list(a3.values())})
# selecting top 10 most frequent hashtags     
d3 = d3.nlargest(columns="Count", n = 5) 
d3.head()
#plt.figure(figsize=(22,10))
#ax = sns.barplot(data=d, x= "Hashtag", y = "Count")
#ax.set(ylabel = 'Count')
#plt.show()
#negative hastags funtion will come over here
b3 = nltk.FreqDist(HT_negative)
e3 = pd.DataFrame({'Hashtag': list(b3.keys()), 'Count': list(b3.values())})
# selecting top 10 most frequent hashtags
e3 = e3.nlargest(columns="Count", n = 5)   
#plt.figure(figsize=(16,5))
#ax = sns.barplot(data=e, x= "Hashtag", y = "Count")
#ax.set(ylabel = 'Count')
#plt.show()'''
g3 = nltk.FreqDist(HT_positive)
h3 = pd.DataFrame({'Hashtag': list(g3.keys()),
                  'Count': list(g3.values())})
# selecting top 10 most frequent hashtags     
h3 = h3.nlargest(columns="Count", n = 5) 

#-------------------------Lockdown4---------------------
HT_regular = hashtag_extract(df4['text'][df4['labels'] == 0])
# extracting hashtags from racist/sexist tweets
HT_negative = hashtag_extract(df4['text'][df4['labels'] == -1])
HT_positive = hashtag_extract(df4['text'][df4['labels'] == 1])
# unnesting list
HT_regular = sum(HT_regular,[])
HT_negative = sum(HT_negative,[])
HT_positive = sum(HT_positive,[])
#print(HT_regular,file=sys.stderr)
#print(HT_negative,file=sys.stderr)
#positive hashtags
a4 = nltk.FreqDist(HT_regular)
d4 = pd.DataFrame({'Hashtag': list(a4.keys()),
                  'Count': list(a4.values())})
# selecting top 10 most frequent hashtags     
d4 = d4.nlargest(columns="Count", n = 5) 
d4.head()
#plt.figure(figsize=(22,10))
#ax = sns.barplot(data=d, x= "Hashtag", y = "Count")
#ax.set(ylabel = 'Count')
#plt.show()
#negative hastags funtion will come over here
b4 = nltk.FreqDist(HT_negative)
e4 = pd.DataFrame({'Hashtag': list(b4.keys()), 'Count': list(b4.values())})
# selecting top 10 most frequent hashtags
e4 = e4.nlargest(columns="Count", n = 5)   
#plt.figure(figsize=(16,5))
#ax = sns.barplot(data=e, x= "Hashtag", y = "Count")
#ax.set(ylabel = 'Count')
#plt.show()'''
g4 = nltk.FreqDist(HT_positive)
h4 = pd.DataFrame({'Hashtag': list(g4.keys()),
                  'Count': list(g4.values())})
# selecting top 10 most frequent hashtags     
h4 = h4.nlargest(columns="Count", n = 5) 

#Use this for wordcount
'''
def word_count(sentence):
    return len(sentence.split())
df['word count'] = df['text'].apply(word_count)
x = df['word count'][df.labels == 1]
y = df['word count'][df.labels == 0]
print(x,file=sys.stderr)
print(y,file=sys.stderr)
#plt.figure(figsize=(12,6))
#plt.xlim(0,45)
#plt.xlabel('word count')
#plt.ylabel('frequency')
#g = plt.hist([x, y], color=['r','b'], alpha=0.5, label=['positive','negative'])
#plt.legend(loc='upper right')
#Till here'''


app.layout =  html.Div([
    dcc.Tabs(id="tabs", value='tab-1', children=[
    dcc.Tab(label='Live Tweets', value='tab-1',children=[dcc.Interval(
        id='interval-component-slow',
        interval=1 * 2000,
        n_intervals=0  # in milliseconds
        )]),
        dcc.Tab(label='Lockdown 1.0', value='tab-2'),
        dcc.Tab(label='Lockdown 2.0', value='tab-3'),
        dcc.Tab(label='Lockdown 3.0', value='tab-4'),
        dcc.Tab(label='Lockdown 4.0', value='tab-5'),
        dcc.Tab(label='Lockdown Analysis', value='tab-6',children = [dcc.Dropdown(
        id='date-dropdown',
        options=[{'label': i, 'value': i} for i in dates['day'].unique()],
        value='25-03-2020',
        multi = False,
        style = {'width': '40%'}

    )]),
    ],
      colors={
                "border":"#eeeeee",
                "primary":"#679b9b",
                "background":"#2e9cc8",

      }
    ),
    html.Div(id='tabs-content')
])
#------------------------------------------DONUT CHART----------------------------------------------------------
count1=(df1['labels'][df1['labels']==1]).count()
count1loc2=(df2['labels'][df2['labels']==1]).count()
count1loc3=(df3['labels'][df3['labels']==1]).count()
count1loc4=(df4['labels'][df4['labels']==1]).count()
countneg=(df1['labels'][df1['labels']==-1]).count()
countneg2=(df2['labels'][df2['labels']==-1]).count()
countneg3=(df3['labels'][df3['labels']==-1]).count()
countneg4=(df4['labels'][df4['labels']==-1]).count()
count0=(df1['labels'][df1['labels']==0]).count()
count0loc2=(df2['labels'][df2['labels']==0]).count()
count0loc3=(df3['labels'][df3['labels']==0]).count()
count0loc4=(df4['labels'][df4['labels']==0]).count()

print(count1)
colors=['#ff9595','royalblue','#80bdab']
#--------------------------------------HASHTAGS SUBPLOTS---------------------------------------------------------
#-----------------Lockdown1--------------------------------
fig = make_subplots(rows=1, cols=3)

fig.add_trace(
    go.Bar(y=e.Hashtag,
                x=e.Count,
                name='# Negative',
                textfont_color='white',
                
                orientation='h'),
    row=1, col=1
)

fig.add_trace(
    go.Bar(y=h.Hashtag,
                x=h.Count,
                name='# Positive',
                textfont_color='white',
                
                orientation='h'),
    row=1, col=2
)

fig.add_trace(
    go.Bar(y=d.Hashtag,
                x=d.Count,
                name='# Neutral',
                textfont_color='white',

                orientation='h'),
    row=1, col=3
)


fig.update_layout( 
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                uniformtext_minsize=8, 
                uniformtext_mode='hide',
                title_text="Popular Hashtags"

                )

#----------------Lockdown2----------------------
figloc2 = make_subplots(rows=1, cols=3)

figloc2.add_trace(
    go.Bar(y=e2.Hashtag,
                x=e2.Count,
                name='# Negative',
                textfont_color='white',
                
                orientation='h'),
    row=1, col=1
)

figloc2.add_trace(
    go.Bar(y=h2.Hashtag,
                x=h2.Count,
                name='# Positive',
                textfont_color='white',
                
                orientation='h'),
    row=1, col=2
)

figloc2.add_trace(
    go.Bar(y=d2.Hashtag,
                x=d2.Count,
                name='# Neutral',
                textfont_color='white',

                orientation='h'),
    row=1, col=3
)



figloc2.update_layout( 
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                uniformtext_minsize=8, 
                uniformtext_mode='hide',
                title_text="Popular Hashtags"

                )

#--------------------Lockdown3-------------------
figloc3 = make_subplots(rows=1, cols=3)

figloc3.add_trace(
    go.Bar(y=e3.Hashtag,
                x=e3.Count,
                name='# Negative',
                textfont_color='white',
                
                orientation='h'),
    row=1, col=1
)

figloc3.add_trace(
    go.Bar(y=h3.Hashtag,
                x=h3.Count,
                name='# Positive',
                textfont_color='white',
                
                orientation='h'),
    row=1, col=2
)

figloc3.add_trace(
    go.Bar(y=d3.Hashtag,
                x=d3.Count,
                name='# Neutral',
                textfont_color='white',

                orientation='h'),
    row=1, col=3
)



figloc3.update_layout( 
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                uniformtext_minsize=8, 
                uniformtext_mode='hide',
                title_text="Popular Hashtags"

                )

#-------------Lockdown4-----------------------
figloc4 = make_subplots(rows=1, cols=3)

figloc4.add_trace(
    go.Bar(y=e4.Hashtag,
                x=e4.Count,
                name='# Negative',
                textfont_color='white',
                
                orientation='h'),
    row=1, col=1
)

figloc4.add_trace(
    go.Bar(y=h4.Hashtag,
                x=h4.Count,
                name='# Positive',
                textfont_color='white',
                
                orientation='h'),
    row=1, col=2
)

figloc4.add_trace(
    go.Bar(y=d4.Hashtag,
                x=d4.Count,
                name='# Neutral',
                textfont_color='white',

                orientation='h'),
    row=1, col=3
)



figloc4.update_layout( 
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                uniformtext_minsize=8, 
                uniformtext_mode='hide',
                title_text="Popular Hashtags"

                )


#----------------------------------------WATSON TONE ANALYSER------------------------------------------------------------
tone=pd.read_csv('lock1ToneAnalyser.csv')
count_sad=tone['sadness'].sum()
count_joy=tone['joy'].sum()
count_confident=tone['confident'].sum()
count_analytical=tone['analytical'].sum()
count_tentative=tone['tentative'].sum()
count_fear=tone['fear'].sum()
count_anger=tone['anger'].sum()

colors_emo=['#ff9595','#ff9595','#ff9595','#80bdab','royalblue','royalblue','royalblue']

fig1 = go.Figure([go.Bar(
             x=['😁','😎','🧐','😐','🥺','😨','😡'],
             y=[count_joy,count_confident,count_analytical,count_tentative,count_sad,count_fear,count_anger],
             hovertext=['Happy','Hopeful','Analytical','Neutral','Sad','Fearful','Angry'],
             hoverinfo='text+y',
             marker_color=colors_emo
             

    )])




fig1.update_layout( title ="Bar Chart",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                uniformtext_minsize=8, 
                uniformtext_mode='hide',
                title_text="Tone Analysis",
                #yaxis_tickformat='percent'
                )
fig1.update_xaxes(tickfont=dict(size=25))

#--------------------Lockdown2----------------------
tone=pd.read_csv('Lock2ToneAnalyser.csv')
count_sad=tone['sadness'].sum()
count_joy=tone['joy'].sum()
count_confident=tone['confident'].sum()
count_analytical=tone['analytical'].sum()
count_tentative=tone['tentative'].sum()
count_fear=tone['fear'].sum()
count_anger=tone['anger'].sum()

colors_emo=['#ff9595','#ff9595','#ff9595','#80bdab','royalblue','royalblue','royalblue']

fig1loc2 = go.Figure([go.Bar(
             x=['😁','😎','🧐','😐','🥺','😨','😡'],
             y=[count_joy,count_confident,count_analytical,count_tentative,count_sad,count_fear,count_anger],
             hovertext=['Happy','Hopeful','Analytical','Neutral','Sad','Fearful','Angry'],
             hoverinfo='text+y',
             marker_color=colors_emo
             

    )])




fig1loc2.update_layout( title ="Bar Chart",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                uniformtext_minsize=8, 
                uniformtext_mode='hide',
                title_text="Tone Analysis",
                #yaxis_tickformat='percent'
                )
fig1loc2.update_xaxes(tickfont=dict(size=25))

#--------------------Lockdown3----------------------
tone=pd.read_csv('Lock3ToneAnalyser.csv')
count_sad=tone['sadness'].sum()
count_joy=tone['joy'].sum()
count_confident=tone['confident'].sum()
count_analytical=tone['analytical'].sum()
count_tentative=tone['tentative'].sum()
count_fear=tone['fear'].sum()
count_anger=tone['anger'].sum()

colors_emo=['#ff9595','#ff9595','#ff9595','#80bdab','royalblue','royalblue','royalblue']

fig1loc3 = go.Figure([go.Bar(
             x=['😁','😎','🧐','😐','🥺','😨','😡'],
             y=[count_joy,count_confident,count_analytical,count_tentative,count_sad,count_fear,count_anger],
             hovertext=['Happy','Hopeful','Analytical','Neutral','Sad','Fearful','Angry'],
             hoverinfo='text+y',
             marker_color=colors_emo
             

    )])




fig1loc3.update_layout( title ="Bar Chart",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                uniformtext_minsize=8, 
                uniformtext_mode='hide',
                title_text="Tone Analysis",
                #yaxis_tickformat='percent'
                )
fig1loc3.update_xaxes(tickfont=dict(size=25))

#----------------Lockdown4-------------------
tone=pd.read_csv('Lock4ToneAnalyser.csv')
count_sad=tone['sadness'].sum()
count_joy=tone['joy'].sum()
count_confident=tone['confident'].sum()
count_analytical=tone['analytical'].sum()
count_tentative=tone['tentative'].sum()
count_fear=tone['fear'].sum()
count_anger=tone['anger'].sum()

colors_emo=['#ff9595','#ff9595','#ff9595','#80bdab','royalblue','royalblue','royalblue']

fig1loc4 = go.Figure([go.Bar(
             x=['😁','😎','🧐','😐','🥺','😨','😡'],
             y=[count_joy,count_confident,count_analytical,count_tentative,count_sad,count_fear,count_anger],
             hovertext=['Happy','Hopeful','Analytical','Neutral','Sad','Fearful','Angry'],
             hoverinfo='text+y',
             marker_color=colors_emo
             

    )])




fig1loc4.update_layout( title ="Bar Chart",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                uniformtext_minsize=8, 
                uniformtext_mode='hide',
                title_text="Tone Analysis",
                #yaxis_tickformat='percent'
                )
fig1loc4.update_xaxes(tickfont=dict(size=25))


#-------------------------------------------------LINE CHART-------------------------------------------------------------
#-----------------Lockdown1-------------------------
df_p1=pd.read_csv('Line Graph/Lock1/df_p1.csv')
df_neg1=pd.read_csv('Line Graph/Lock1/df_neg1.csv')
df_neu1=pd.read_csv('Line Graph/Lock1/df_neu1.csv')
fig2=go.Figure()
    
#fig2=tools.make_subplots(rows=1,cols=3,shared_xaxes=True,shared_yaxes=True)
fig2.add_trace(go.Scatter(x=df_neg1.day,
    y=df_neg1.neg,name='negatives'))
fig2.add_trace(go.Scatter(x=df_p1['day'],
    y=df_p1['pos'],name='positives'))

fig2.add_trace(go.Scatter( x=df_neu1.day,
    y=df_neu1.neu,name='neutrals'))

fig2['layout'].update( title ="Line Chart",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                #uniformtext_minsize=8, 
                #uniformtext_mode='hide',
                title_text="Emotional Trends in Lockdown 1.0",
                #yaxis_tickformat='percent'
                )

#-----------Lockdown2----------------
df_p2=pd.read_csv('Line Graph/Lock2/df_p2.csv')
df_neg2=pd.read_csv('Line Graph/Lock2/df_neg2.csv')
df_neu2=pd.read_csv('Line Graph/Lock2/df_neu2.csv')
fig2loc2=go.Figure()
    
#fig2=tools.make_subplots(rows=1,cols=3,shared_xaxes=True,shared_yaxes=True)
fig2loc2.add_trace(go.Scatter(x=df_neg2.day,
    y=df_neg2.neg,name='negatives'))
fig2loc2.add_trace(go.Scatter(x=df_p2['day'],
    y=df_p2['pos'],name='positives'))

fig2loc2.add_trace(go.Scatter( x=df_neu2.day,
    y=df_neu2.neu,name='neutrals'))

fig2loc2['layout'].update( title ="Line Chart",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                #uniformtext_minsize=8, 
                #uniformtext_mode='hide',
                title_text="Emotional Trends in Lockdown 1.0",
                #yaxis_tickformat='percent'
                )

#----------------Lockdown3------------------------
df_p3=pd.read_csv('Line Graph/Lock3/df_p3.csv')
df_neg3=pd.read_csv('Line Graph/Lock3/df_neg3.csv')
df_neu3=pd.read_csv('Line Graph/Lock3/df_neu3.csv')
fig2loc3=go.Figure()
    
#fig2=tools.make_subplots(rows=1,cols=3,shared_xaxes=True,shared_yaxes=True)
fig2loc3.add_trace(go.Scatter(x=df_neg3.day,
    y=df_neg3.neg,name='negatives'))
fig2loc3.add_trace(go.Scatter(x=df_p3['day'],
    y=df_p3['pos'],name='positives'))

fig2loc3.add_trace(go.Scatter( x=df_neu3.day,
    y=df_neu3.neu,name='neutrals'))

fig2loc3['layout'].update( title ="Line Chart",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                #uniformtext_minsize=8, 
                #uniformtext_mode='hide',
                title_text="Emotional Trends in Lockdown 1.0",
                #yaxis_tickformat='percent'
                )

#------------Lockdown4-----------
df_p4=pd.read_csv('Line Graph/Lock4/df_p4.csv')
df_neg4=pd.read_csv('Line Graph/Lock4/df_neg4.csv')
df_neu4=pd.read_csv('Line Graph/Lock4/df_neu4.csv')
fig2loc4=go.Figure()
    
#fig2=tools.make_subplots(rows=1,cols=3,shared_xaxes=True,shared_yaxes=True)
fig2loc4.add_trace(go.Scatter(x=df_neg4.day,
    y=df_neg4.neg,name='negatives'))
fig2loc4.add_trace(go.Scatter(x=df_p4['day'],
    y=df_p4['pos'],name='positives'))

fig2loc4.add_trace(go.Scatter( x=df_neu4.day,
    y=df_neu4.neu,name='neutrals'))

fig2loc4['layout'].update( title ="Line Chart",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                #uniformtext_minsize=8, 
                #uniformtext_mode='hide',
                title_text="Emotional Trends in Lockdown 1.0",
                #yaxis_tickformat='percent'
                )

#fig2.update_xaxes(tickfont=dict(size=5))
#-----------------------------------------------------------------------------------------------------------
#----------------------------------------------THANKFUL-------------------------------------------------------------
d1=pd.read_csv('Hashtag Analysis/Thank You/Lock1.csv')
d2=pd.read_csv('Hashtag Analysis/Thank You/Lock2.csv')
d3=pd.read_csv('Hashtag Analysis/Thank You/Lock3.csv')
d4=pd.read_csv('Hashtag Analysis/Thank You/Lock4.csv')
ty_lock1_pos=(d1['labels'][d1['labels']==1]).count()
ty_lock1_neg=(d1['labels'][d1['labels']==-1]).count()
ty_lock1_neu=(d1['labels'][d1['labels']==0]).count()
ty_lock2_pos=(d2['labels'][d2['labels']==1]).count()
ty_lock2_neg=(d2['labels'][d2['labels']==-1]).count()
ty_lock2_neu=(d2['labels'][d2['labels']==0]).count()
ty_lock3_pos=(d3['labels'][d3['labels']==1]).count()
ty_lock3_neg=(d3['labels'][d3['labels']==-1]).count()
ty_lock3_neu=(d3['labels'][d3['labels']==0]).count()
ty_lock4_pos=(d4['labels'][d4['labels']==1]).count()
ty_lock4_neg=(d4['labels'][d4['labels']==-1]).count()
ty_lock4_neu=(d4['labels'][d4['labels']==0]).count()

lockdown=['Lockdown 1.0', 'Lockdown 2.0', 'Lockdown 3.0','Lockdown 4.0']
totallock1 = ty_lock1_pos+ty_lock1_neg+ty_lock1_neu
totallock2 = ty_lock2_pos+ty_lock2_neg+ty_lock2_neu
totallock3 = ty_lock3_pos+ty_lock3_neg+ty_lock3_neu
totallock4 = ty_lock3_pos+ty_lock4_neg+ty_lock4_neu

figty = go.Figure(data=[
    go.Bar(name='Negative', x=lockdown,y=['0.8','0.09','0.33','0.98'],textposition='auto'),
    go.Bar(name='Positive', x=lockdown,y=['0.77','0.77','0.3','0.44'],textposition='auto'),
    go.Bar(name='Neutral', x=lockdown,y=['0.77','0.77','0.3','0.44'],textposition='auto')

])
# Change the bar mode
figty.update_layout(barmode='group',
                title ="Line Chart",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                #uniformtext_minsize=8, 
                #uniformtext_mode='hide',
                title_text="Emotional Trends in Lockdown 1.0",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                yaxis_tickformat=',.0%',
                yaxis_range=[0,1]


    )
figty.update_yaxes(showticklabels=True)
#-------------------------------------------------------------------------------------------------------------------
#----------------------------------------------NEGATIVE-------------------------------------------------------------
d1=pd.read_csv('./China/Lock1.csv')
d2=pd.read_csv('./China/Lock2.csv')
d3=pd.read_csv('./China/Lock3.csv')
d4=pd.read_csv('./China/Lock4.csv')
china_lock1_pos=(d1['labels'][d1['labels']==1]).count()
china_lock1_neg=(d1['labels'][d1['labels']==-1]).count()
china_lock2_pos=(d2['labels'][d2['labels']==1]).count()
china_lock2_neg=(d2['labels'][d2['labels']==-1]).count()
china_lock3_pos=(d3['labels'][d3['labels']==1]).count()
china_lock3_neg=(d3['labels'][d3['labels']==-1]).count()
china_lock4_pos=(d4['labels'][d4['labels']==1]).count()
china_lock4_neg=(d4['labels'][d4['labels']==-1]).count()

lockdown=['Lockdown 1.0', 'Lockdown 2.0', 'Lockdown 3.0','Lockdown 4.0']

figchina = go.Figure(data=[
    go.Bar(name='Negative', x=lockdown,y=['0.8','0.09','0.33','0.98'],textposition='auto'),
    go.Bar(name='Positive', x=lockdown,y=['0.77','0.77','0.3','0.44'],textposition='auto')
])
# Change the bar mode
figchina.update_layout(barmode='group',
                title ="Line Chart",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                #uniformtext_minsize=8, 
                #uniformtext_mode='hide',
                title_text="Emotional Trends in Lockdown 1.0",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                yaxis_tickformat=',.0%',
                yaxis_range=[0,1]


    )
figchina.update_yaxes(showticklabels=True)
#-------------------------------------------------------------------------------------------------------------------
#----------------------------------------------WFH-------------------------------------------------------------
d1=pd.read_csv('./China/Lock1.csv')
d2=pd.read_csv('./China/Lock2.csv')
d3=pd.read_csv('./China/Lock3.csv')
d4=pd.read_csv('./China/Lock4.csv')
china_lock1_pos=(d1['labels'][d1['labels']==1]).count()
china_lock1_neg=(d1['labels'][d1['labels']==-1]).count()
china_lock2_pos=(d2['labels'][d2['labels']==1]).count()
china_lock2_neg=(d2['labels'][d2['labels']==-1]).count()
china_lock3_pos=(d3['labels'][d3['labels']==1]).count()
china_lock3_neg=(d3['labels'][d3['labels']==-1]).count()
china_lock4_pos=(d4['labels'][d4['labels']==1]).count()
china_lock4_neg=(d4['labels'][d4['labels']==-1]).count()

lockdown=['Lockdown 1.0', 'Lockdown 2.0', 'Lockdown 3.0','Lockdown 4.0']

figchina = go.Figure(data=[
    go.Bar(name='Negative', x=lockdown,y=['0.8','0.09','0.33','0.98'],textposition='auto'),
    go.Bar(name='Positive', x=lockdown,y=['0.77','0.77','0.3','0.44'],textposition='auto')
])
# Change the bar mode
figchina.update_layout(barmode='group',
                title ="Line Chart",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                #uniformtext_minsize=8, 
                #uniformtext_mode='hide',
                title_text="Emotional Trends in Lockdown 1.0",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                yaxis_tickformat=',.0%',
                yaxis_range=[0,1]


    )
figchina.update_yaxes(showticklabels=True)
#-------------------------------------------------------------------------------------------------------------------
#----------------------------------------------GOVT-------------------------------------------------------------
d1=pd.read_csv('./China/Lock1.csv')
d2=pd.read_csv('./China/Lock2.csv')
d3=pd.read_csv('./China/Lock3.csv')
d4=pd.read_csv('./China/Lock4.csv')
china_lock1_pos=(d1['labels'][d1['labels']==1]).count()
china_lock1_neg=(d1['labels'][d1['labels']==-1]).count()
china_lock2_pos=(d2['labels'][d2['labels']==1]).count()
china_lock2_neg=(d2['labels'][d2['labels']==-1]).count()
china_lock3_pos=(d3['labels'][d3['labels']==1]).count()
china_lock3_neg=(d3['labels'][d3['labels']==-1]).count()
china_lock4_pos=(d4['labels'][d4['labels']==1]).count()
china_lock4_neg=(d4['labels'][d4['labels']==-1]).count()

lockdown=['Lockdown 1.0', 'Lockdown 2.0', 'Lockdown 3.0','Lockdown 4.0']

figchina = go.Figure(data=[
    go.Bar(name='Negative', x=lockdown,y=['0.8','0.09','0.33','0.98'],textposition='auto'),
    go.Bar(name='Positive', x=lockdown,y=['0.77','0.77','0.3','0.44'],textposition='auto')
])
# Change the bar mode
figchina.update_layout(barmode='group',
                title ="Line Chart",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                #uniformtext_minsize=8, 
                #uniformtext_mode='hide',
                title_text="Emotional Trends in Lockdown 1.0",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                yaxis_tickformat=',.0%',
                yaxis_range=[0,1]


    )
figchina.update_yaxes(showticklabels=True)
#-------------------------------------------------------------------------------------------------------------------
#----------------------------------------------EXTEND-------------------------------------------------------------
d1=pd.read_csv('./China/Lock1.csv')
d2=pd.read_csv('./China/Lock2.csv')
d3=pd.read_csv('./China/Lock3.csv')
d4=pd.read_csv('./China/Lock4.csv')
china_lock1_pos=(d1['labels'][d1['labels']==1]).count()
china_lock1_neg=(d1['labels'][d1['labels']==-1]).count()
china_lock2_pos=(d2['labels'][d2['labels']==1]).count()
china_lock2_neg=(d2['labels'][d2['labels']==-1]).count()
china_lock3_pos=(d3['labels'][d3['labels']==1]).count()
china_lock3_neg=(d3['labels'][d3['labels']==-1]).count()
china_lock4_pos=(d4['labels'][d4['labels']==1]).count()
china_lock4_neg=(d4['labels'][d4['labels']==-1]).count()

lockdown=['Lockdown 1.0', 'Lockdown 2.0', 'Lockdown 3.0','Lockdown 4.0']

figchina = go.Figure(data=[
    go.Bar(name='Negative', x=lockdown,y=['0.8','0.09','0.33','0.98'],textposition='auto'),
    go.Bar(name='Positive', x=lockdown,y=['0.77','0.77','0.3','0.44'],textposition='auto')
])
# Change the bar mode
figchina.update_layout(barmode='group',
                title ="Line Chart",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                #uniformtext_minsize=8, 
                #uniformtext_mode='hide',
                title_text="Emotional Trends in Lockdown 1.0",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                yaxis_tickformat=',.0%',
                yaxis_range=[0,1]


    )
figchina.update_yaxes(showticklabels=True)
#-------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------OVERALL Sentiment-----------------------------------------------
figoverall = make_subplots(rows=1, cols=3)

figoverall.add_trace(
    go.Bar(y=[100,50,70,89],
                x=lockdown,
                name='# Negative',
                textfont_color='white',
                
                #orientation='h'
                ),
    row=1, col=1
)

figoverall.add_trace(
    go.Bar(y=[100,50,70,89],
                x=lockdown,
                name='# Positive',
                textfont_color='white',
                
                #orientation='h'
                ),
    row=1, col=2
)

figoverall.add_trace(
    go.Bar(y=[100,50,70,89],
                x=lockdown,
                name='# Neutral',
                textfont_color='white',

                #orientation='h'
                ),
    row=1, col=3
)



figoverall.update_layout( title ="Bar Chart",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a",
                plot_bgcolor="#07031a",
                uniformtext_minsize=8, 
                uniformtext_mode='hide',
                title_text="Popular Hashtags"

                )
#----------------------------------------------------------------------------------------------
@app.callback(Output('tabs-content', 'children'),
            [Input('tabs', 'value'),
              Input('date-dropdown', 'value'),
              Input('interval-component-slow', 'n_intervals')])
def render_content(tab,sel_option,n):
    sel = dates[dates['day']==sel_option]
    global positive
    global negative
    global neutral
    global db
    global old_time
    global old_tweet
    content='hi'
        # print(cal)
    #uncomment for local
    # try:
    #         df=pd.read_json('count.json')
    #         print(df['details'][0]['tweet'])
    # except:
    #         print("cant")

    result_collection = Result(db.all_docs, include_docs=True)
    # print(len(list(result_collection)))
    # rc=result_collection
    c = len(list(result_collection)) - 1
    # print(f"Retrieved full document:\n{result_collection[c]}\n")

    # print(result_collection[c][0]['doc']['tweet'])

    global pos
    global neg
    global time
    global tf2
    # positive = rc[c][0]['doc']['positive']
    #
    # negative = rc[c][0]['doc']['negative']
    # neutral = rc[c][0]['doc']['neutral']
    # neutral=0

    # tm.sleep(0.2)
    labels = result_collection[c][0]['doc']['labels']
    # print(labels)
    # tm.sleep(0.5)
    tweet = result_collection[c][0]['doc']['tweet']

    if tweet != old_tweet:
        if labels == 1:
            positive+=1
        elif labels==-1:
            negative+=1
        else:
            neutral+=1
        old_tweet = tweet
    time = result_collection[c][0]['doc']['time']
    # if tweet == old_tweet and time == old_time:
    #     if labels == 1:
    #         positive-=1
    #     elif labels==-1:
    #         negative-=1
    #     else:
    #         neutral-=1
    # else:
    #     old_tweet=tweet

    cal.loc[cal['val'] == 'positive', 'count'] = positive
    cal.loc[cal['val'] == 'negative', 'count'] = negative
    cal.loc[cal['val'] == 'neutral', 'count'] = neutral

    # time=9
    print(tweet)
    hashtags = result_collection[c][0]['doc']['hashtags']
    temp = {'pos': positive, 'neg': negative, 'neu': neutral, 'time': time,'text':tweet,'label':labels,'hashtags':hashtags}
    # print(temp)
    temp = pd.DataFrame(temp, columns=['pos', 'neg', 'neu', 'time','text','label','hashtags'], index=[[1]])
    # print(temp)
    tf2 = pd.concat([tf2, temp], ignore_index=True)
    tf2.drop_duplicates(subset=['text'],inplace=True)
    print(tf2)
    print(len(tf2))


    x=list([20,30,204,309])
    y=list([90,345,234,234])
    # if time != cal['time'][0]:
    # cal['time'][0] = time
    figlive=px.bar(cal,x='val',y='count')
        # fig2=px.scatter(tf,x='time',y=[['pos','neg']],color=[['pos','neg']])
    figlive2=px.scatter(tf2,x='time',y=['neg','pos','neu'])
    if tab == 'tab-1':
       return html.Div([

            html.Div([
           dcc.Graph(id='trend2',
            figure=figlive),
            
    ], style={'display':'block','padding':'0 0 0 20'}),
            html.Div([
           dcc.Graph(id='trend2',
            figure=figlive2),
], style={'display':'block','padding':'0 0 0 20'})

            ])
        
    elif tab == 'tab-6':
       return html.Div([
      html.Div([
                  dcc.Graph(
                      id="scatter_chart",
                      figure = {
                          'data': [
                              go.Scatter(
                                  x = sel['time'],
                                  y = sel['labels'],
                                  mode='markers'
                              )
                          ],
                          'layout' : go.Layout(
                              title = "ScatterPlot",
                              xaxis =  {'title': 'Time'},
                              yaxis = {'title': 'Sentiments'},
                              paper_bgcolor ="#07031a"
                          )
                      }
                  )
        ],style={'display':'block','padding':'0 0 0 20'}),
       
       html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=figchina,
         )]
            ,style={'width':'50%','display':'inline-block','padding':'0 0 0 20'}),

        html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=figchina,
         )]
            ,style={'width':'50%','display':'inline-block','padding':'0 0 0 20'}),

       
       html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=figoverall,
         )]
            ,style={'display':'block','padding':'0 0 0 20'}),
    



            


        ])
    elif tab == 'tab-2':
       return html.Div([
        
html.Div([
            dcc.Graph(
            id="pie_chart",
            figure=
         {
            'data':[
            go.Pie(
                labels=['positives','negatives','neutrals'],
                hole=.8,

                values=[count1,countneg,count0],
                name="Sentiment Analysis",
                hoverinfo='label+percent',
                textinfo='label+percent',
                insidetextorientation='radial',
                textfont_color='white',
                marker=dict(colors=colors))],
            'layout':go.Layout(
                title ="Emotion Distribution",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a"
                )})]
            ,style={'width':'50%','display':'inline-block','padding':'0 0 0 20'}),


html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=fig1,
         )]
            ,style={'width':'50%','display':'inline-block','padding':'0 0 0 20'}),

html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=fig,
         )]
            ,style={'display':'block','padding':'0 0 0 20'}),

html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=fig2,
         )]
            ,style={'display':'block','padding':'0 0 0 20'}),


html.Div([
        html.Img(src=app.get_asset_url('lock1neg.png')),
        html.Img(src=app.get_asset_url('lock1pos.png')) 

         ]

        ,style={'width':'100%','display':'block','padding':'0 0 0 20'}),





        ],style={'background':'#25274d'})

        
    elif tab == 'tab-3':
       return html.Div([
        
html.Div([
            dcc.Graph(
            id="pie_chart",
            figure=
         {
            'data':[
            go.Pie(
                labels=['positives','negatives','neutrals'],
                hole=.8,

                values=[count1loc2,countneg2,count0loc2],
                name="Sentiment Analysis",
                hoverinfo='label+percent',
                textinfo='label+percent',
                insidetextorientation='radial',
                textfont_color='white',
                marker=dict(colors=colors))],
            'layout':go.Layout(
                title ="Emotion Distribution",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a"
                )})]
            ,style={'width':'50%','display':'inline-block','padding':'0 0 0 20'}),


html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=fig1loc2,
         )]
            ,style={'width':'50%','display':'inline-block','padding':'0 0 0 20'}),

html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=figloc2,
         )]
            ,style={'display':'block','padding':'0 0 0 20'}),

html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=fig2loc2,
         )]
            ,style={'display':'block','padding':'0 0 0 20'}),


html.Div([ 
        html.Img(src=app.get_asset_url('lock2neg.png')),
        html.Img(src=app.get_asset_url('lock2pos.png')) 

         ]

        ,style={'width':'100%','display':'block','padding':'0 0 0 50'}),





        ],style={'background':'#25274d'})

        
    elif tab == 'tab-4':
       return html.Div([
        
html.Div([
            dcc.Graph(
            id="pie_chart",
            figure=
         {
            'data':[
            go.Pie(
                labels=['positives','negatives','neutrals'],
                hole=.8,

                values=[count1loc3,countneg3,count0loc3],
                name="Sentiment Analysis",
                hoverinfo='label+percent',
                textinfo='label+percent',
                insidetextorientation='radial',
                textfont_color='white',
                marker=dict(colors=colors))],
            'layout':go.Layout(
                title ="Emotion Distribution",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a"
                )})]
            ,style={'width':'50%','display':'inline-block','padding':'0 0 0 20'}),


html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=fig1loc3,
         )]
            ,style={'width':'50%','display':'inline-block','padding':'0 0 0 20'}),

html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=figloc3,
         )]
            ,style={'display':'block','padding':'0 0 0 20'}),

html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=fig2loc3,
         )]
            ,style={'display':'block','padding':'0 0 0 20'}),


html.Div([ 
        html.Img(src=app.get_asset_url('lock3neg.png')),
        html.Img(src=app.get_asset_url('lock3pos.png')) 

         ]

        ,style={'width':'100%','display':'block','padding':'0 0 0 50'}),





        ],style={'background':'#25274d'})

        
    elif tab == 'tab-5':
       return html.Div([
        
html.Div([
            dcc.Graph(
            id="pie_chart",
            figure=
         {
            'data':[
            go.Pie(
                labels=['positives','negatives','neutrals'],
                hole=.8,

                values=[count1loc4,countneg4,count0loc4],
                name="Sentiment Analysis",
                hoverinfo='label+percent',
                textinfo='label+percent',
                insidetextorientation='radial',
                textfont_color='white',
                marker=dict(colors=colors))],
            'layout':go.Layout(
                title ="Emotion Distribution",
                font=dict(
                    family="Courier New,monospace",
                    size=14,
                    color='white'

                      ),

                paper_bgcolor ="#07031a"
                )})]
            ,style={'width':'50%','display':'inline-block','padding':'0 0 0 20'}),


html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=fig1loc4,
         )]
            ,style={'width':'50%','display':'inline-block','padding':'0 0 0 20'}),

html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=figloc4,
         )]
            ,style={'display':'block','padding':'0 0 0 20'}),

html.Div([
            dcc.Graph(
            id="bar_chart",
            figure=fig2loc4,
         )]
            ,style={'display':'block','padding':'0 0 0 20'}),


html.Div([ 
        html.Img(src=app.get_asset_url('lock4neg.png')),
        html.Img(src=app.get_asset_url('lock4pos.png')) 

         ]

        ,style={'width':'100%','display':'block','padding':'0 0 0 50'}),





        ],style={'background':'#25274d'})

if __name__ == '__main__':
    app.run_server(host='localhost', port=port,debug=True)
