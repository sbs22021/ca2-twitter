import warnings
import tweetnlp
import pandas as pd
import pyspark
import numpy as np
from tqdm import tqdm
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession, SQLContext
from pyspark.sql.types import IntegerType, StringType, StructType, StructField, DoubleType
from pyspark.sql.functions import udf
from pyspark.sql.functions import monotonically_increasing_id
from pymongo import MongoClient
warnings.filterwarnings("ignore")
tqdm.pandas()

mongo_uri = "mongodb://hadoop-vm.internal.cloudapp.net:27017/ca2"

# Spark version 3.2.3
# MongoDB version 6.0.5
# Java Version 11

# create a spark session
# Jars dependencies available in maven repository
# https://mvnrepository.com/search?q=mongodb-driver-sync
spark = SparkSession.builder \
    .appName('Tweets') \
    .config("spark.mongodb.read.connection.uri", mongo_uri) \
    .config("spark.mongodb.write.connection.uri", mongo_uri) \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.1.1") \
    .config("spark.jars.packages", "org.mongodb:mongodb-driver-core:4.9.1") \
    .config("spark.jars.packages", "org.mongodb:mongodb-driver-sync:4.9.1") \
    .config("spark.jars.packages", "org.mongodb:bson:4.9.1") \
    .getOrCreate()


# read data from mongodb collection "tweets" into a dataframe "df"
df = spark.read \
    .format("mongodb") \
    .option("connection.uri", mongo_uri) \
    .option("database", "ca2") \
    .option("collection", "vaccin_tweets_2") \
    .load()

print(f"Loading Roberta Model")
model = tweetnlp.Sentiment()

# Preprocess tweets to remove user info and any web url as Roberta 
def parse_tweet(tweet):
    new_text = []
    for t in tweet.split(" "):
        t = "@user" if t.startswith("@") and len(t) > 1 else t
        t = "http" if t.startswith("http") else t
        new_text.append(t)
    return " ".join(new_text)

# generate sentiment scores
def sentiment_analyzer(text, model):
    output = model.sentiment(text, return_probability=True)
    return (output['label'], output['probability'][output['label']])

def process_data(df, start_index, end_index, skip_to=0):
    total_count = df_pd['_id'].count()
    num_batches = (total_count // batch_size) + 1

    for i in range(num_batches):
        start = i * batch_size
        end = start + batch_size
        if(start < skip_to):
            continue
        
        # Select the batch of data
        batch_df = df[(df['index'] >= start) & (df['index'] < end)]
        
        # Apply the sentiment function to 'text' column
        batch_df['sentiment'], batch_df['s_probability'] = zip(*batch_df['text'].progress_apply(lambda x: sentiment_analyzer(x,model)))
        
        # Convert the pandas DataFrame to a list of dictionaries
        data_to_insert = batch_df[['_id','sentiment','s_probability']].to_dict('records')

        # Insert data into MongoDB
        collection.insert_many(data_to_insert)
        print(f"processed {end} of {total_count} - {round((end / total_count)):.2%}")


# Add index to your dataframe
df = df.withColumn("index", monotonically_increasing_id())
print(f"Loading tweets in memory")
df_pd = df.toPandas()
df_pd = df_pd[['_id','text','index']]
df_pd['text'] = df_pd['text'].apply(lambda x: parse_tweet(x))

client = MongoClient(mongo_uri)
db = client["ca2"]
collection = db["vaccin_tweets_2_sentiment"]

batch_size = 2000
start_index = 0
end_index = df_pd['index'].max()

print(f"Starting process_data")
process_data(df_pd,start_index,end_index,skip_to=292000)

print(f"*****End******")
client.close()
        