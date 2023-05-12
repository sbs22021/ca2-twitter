import pyspark
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession, SQLContext, functions as F
from pyspark.sql.types import IntegerType, StringType
from pyspark.ml.feature import Tokenizer, StopWordsRemover
from pyspark.ml.feature import HashingTF, IDF
import tweetnlp
import pandas as pd
from tqdm import tqdm

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
    .option("collection", "vaccin_tweets") \
    .load()


print("Preparing sentiment model")
model = tweetnlp.Sentiment()

# Convert to pandas
tqdm.pandas()
pd_df = df.toPandas()
print("Starting....")
pd_df['sentiment'] = pd_df['text'].progress_apply(lambda x: model.predict(x))

print("Saving to parquet....")
pd_df.to_parquet('df.parquet.gzip', compression='gzip')  