from cloudant import Cloudant #!!COMMENTED FROM BHUSHAN'S CODE!!
import time
import atexit #!!COMMENTED FROM BHUSHAN'S CODE!!
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
from datetime import datetime
from datetime import timedelta
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
from nltk.corpus import stopwords
# import re
import string
import os
from cloudant import Cloudant
from flask import Flask, render_template, request, jsonify
import atexit
import os
import json



app = Flask(__name__, static_url_path='')

db_name = 'live'
client = None
db = None

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        apikey= creds['apikey']
        url = 'https://' + creds['host']
        client = Cloudant.iam(user,apikey,url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif "CLOUDANT_URL" in os.environ:
    client = Cloudant.iam(os.environ['CLOUDANT_USERNAME'], os.environ['CLOUDANT_APIKEY'], url=os.environ['CLOUDANT_URL'], connect=True)
    db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['apikey']
        url = 'https://' + creds['host']
        client = Cloudant.iam(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)


# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000




# /**
#  * Endpoint to get a JSON array of all the visitors in the database
#  * REST API example:
#  * <code>
#  * GET http://localhost:8000/api/visitors
#  * </code>
#  *
#  * Response:
#  * [ "Bob", "Jane" ]
#  * @return An array of all the visitor names
#  */

# sampleData = [
#     [1, "one", "boiling", 100],
#     [2, "two", "hot", 40],
#     [3, "three", "warm", 20],
#     [4, "four", "cold", 10],
#     [5, "five", "freezing", 0]
# ]

# for document in sampleData:
#     # Retrieve the fields in each row.
#     number = document[0]
#     name = document[1]
#     description = document[2]
#     temperature = document[3]

    # Create a JSON document that represents
    # all the data in the row.
    # jsonDocument = {
    #     "numberField": number,
    #     "nameField": name,
    #     "descriptionField": description,
    #     "temperatureField": temperature
    # }

    # Create a document using the Database API.






















"# -- coding: utf-8 --"
# vector = pickle.load(open('vec', 'rb'))
# vectorizer=vector['vector']
vectorizer = pickle.load(open("vector.pickel", "rb"))
w = pickle.load(open('train', 'rb'))
x_train=w['x_train']
vectorizer.fit(x_train)
print(vectorizer)
print(len(vectorizer.get_feature_names()))
filename = 'logR.sav'

# filename='logR.sav'
loaded_model = joblib.load(open(filename, 'rb'))
def calctime(a):
    return time.time() - a


positive = 0
negative = 0
neutral = 0
compound=0

count = 0
initime = time.time()

ps = PorterStemmer()
wnl = WordNetLemmatizer()


ckey = 'WnyAgUaacX1YheRSJqwMhhZgR'
csecret = 'LzHg7GuAfJNIsHRpRXEk72TaEjcG5RL9yl85c0rbI1V1pg6rHQ'
atoken = "1125091796046843905-DNeIxEe9RNwlwzZZXwXEW3VJFlv7Az"
asecret = "n3Yc9GzA2Saa6LNPZ5465WdQNj06G6hBrqcWnpwkc4jCb"

js=pd.DataFrame(columns=['text','labels'])
tl=[]
id="1"
class listener(StreamListener):

    def on_data(self, data):
        global initime
        global tl
        global id
        hashtags=[]
        all_data = json.loads(data)
        tweet = all_data["text"]
        try:
            for i in all_data['entities']['hashtags']:
                hashtags.append(i['text'])
            print("hastags ",hashtags)
        except:
            pass
        dt = all_data['created_at']
        dt = dt.split(" ")
        local_datetime = datetime.now()
        dt = dt[3]
        dt = datetime.strptime(dt, '%H:%M:%S').time()
        tmp_datetime = datetime.combine(datetime.today(), dt)
        dt = (tmp_datetime + timedelta(hours=5, minutes=30)).time()
        # username=all_data["user"]["screen_name"]
        # tweet = " ".join(re.findall("[a-zA-Z]+", tweet))
        #
        global db
        # print(tweet)
        global ps
        global wnl

        sequencePattern = r"(.)\1\1+"
        seqReplacePattern = r"\1\1"
        tweets = " ".join(filter(lambda x: x[0] != '@', tweet.split()))
        tweets = re.sub(r'([^a-zA-Z0-9])', ' ', tweets)
        tweets = re.sub(r'[^\w\s]', '', tweets)
        #     tweets=re.sub('[\s][a-z]{1,3}[\s]',' ',tweets)
        #     tweets=re.sub('^[a-z]{1,3}[\s]',' ',tweets)
        tweets = re.sub(r'[0-9_]', '', tweets)
        tweets = re.sub(r'^https?:\/\/.*[\r\n]*', '', tweets)
        tweets = re.sub(r"http\S+", "", tweets)
        tweets = tweets.lower()
        tweets = re.sub(sequencePattern, seqReplacePattern, tweets)
        #     print(tweets)
        tweets = tweets.split()
        tweets = [word for word in tweets if not word in set(stopwords.words('english'))]
        tweets = [lemma.lemmatize(word) for word in tweets]

        tweets = " ".join(tweets)

        #     print(tweets[0])
        #     tweets=tweets.split(" ")

        tweets = word_tokenize(tweets)
        #     print(tweets)
        t = []
        for j in tweets:
            #
            t.append(ps.stem(j))
            #            t.append(wnl.lemmatize(j))
            t.append(" ")

        tweets = " ".join(t)
        #     tweets = tweets.split()
        tweets = tweets.replace('ing', '')
        tweets = tweets.replace('pic', '')
        tweets = tweets.replace('com', '')

        # l = vectorizer.transform(tweets).toarray()
        # tweets='fuck corona'
        k = pd.Series(tweets)
        print(k)

        l = vectorizer.transform(k).toarray()
        # print(l)
        m=loaded_model.predict(l)
        print(m[0])
        t = int(calctime(initime))
        # blob = TextBlob(tweet.strip())
        print(t)
        # print(loaded_model)
        # print(vectorizer)
        # tl.append({'tweet':tweet,'label':m[0]})
        global positive
        global negative
        global neutral
        global count
        global compound
        count = count + 1
        # senti = 0
        # for sen in blob.sentences:
        #     senti = senti + sen.sentiment.polarity
        #     if sen.sentiment.polarity >= 0:
        #         positive = positive + sen.sentiment.polarity
        #     else:
        #         negative = negative + sen.sentiment.polarity
        # compound = compound + senti
        # print
        # count
        # print
        if m[0]==1:
            positive=positive+1
        elif m[0]==-1:
            negative=negative+1
        else:
            neutral=neutral+1

        print("pos ",positive)
        print("neg",negative)
        print("neu",neutral)
        # k={"_id":count,"pos":positive,"neg":negative,"time":t,"details":tl}
        k=str(k)

        label=int(m[0])
        id=id+"1"
            # Retrieve the fields in each row.
        # number = positive
        # name = negative
        # description = t
        # temperature = tl
            #
            # Create a JSON document that represents
            # all the data in the row.
        json_document = {
                "_id":id,
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
                "hashtags":[hashtags],
                "time":str(dt),
                "tweet":k,
                "labels":label
                # "temperatureField": temperature
            }
            #
            # Create a document by using the database API.
        new_document = db.create_document(json_document)
            #
            # Check that the document exists in the database.
        if new_document.exists():
                print(f"Document '{positive}' successfully created.")
        # jsonDocument = k
        # newDocument = db.create_document(k)
        # db.create_document(k)
        # u=positive+negative+neutral
        sen=[positive,negative,neutral]
        # print(sen)
        xsen=['positive','negative','neutral','time']
        tweets.strip()
        # print
        # senti
        # print
        # t
        # print
        # str(positive) + ' ' + str(negative) + ' ' + str(neutral)
        # print(len(t))
        # plt.axis([ 0, 70,0,220])
        # plt.xlabel('Time')
        # plt.ylabel('Sentiment')
        # plt.plot([t],[positive],'go',[t] ,[negative],'ro',[t],[neutral],'bo')
        # plt.plot([t],[u])
        width = 0.35
        # plt.bar(xsen,sen,width = 0.35,color='r')

        # plt.show()
        # plt.pause(0.0001)
        # temp={'text':tweet,'labels':m}
        # js=pd.DataFrame(temp)
        #
        # js.append(temp,ignore_index=True)
        # try:
        #     print(js)
        #     js.to_json('obj.json')
        # except:
        #     print("cannot")
        #     pass
        if count == 50:
            return False

        else:
            return True

    def on_error(self, status_code):
        if status_code == 420:
            # return False to disconnect the stream
           return False


auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener(count),lang='en',geocode="22.3511148,78.6677428,1km")
twitterStream.filter(track=["#IndiaFightsCorona","covid19 india","corona india","#covid19#india","corona warriors","#cluelessbjp"])

        # time.sleep(5)
		
port = int(os.getenv('PORT', 8000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)


