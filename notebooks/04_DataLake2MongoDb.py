import json
from hdfs import InsecureClient
from pymongo import MongoClient

# MONGODB
mongo_url = 'mongodb://hadoop-vm.internal.cloudapp.net:27017/ca2.tweets'
database_name = 'ca2'
collection_name = 'tweets'

# HADOOP
hdfs_url = 'http://hadoop-vm.internal.cloudapp.net:9870'
hdfs_directory = "/twitter"

# Connect to Hadoop
client = InsecureClient(hdfs_url, user='hduser')

# Connect to MongoDB
mongo_client = MongoClient(mongo_url)
db = mongo_client[database_name]
collection = db[collection_name]

# List JSON files in Hadoop directory
json_files = client.list(hdfs_directory)

# Read JSON files and insert into MongoDB
for file_name in json_files:
    if file_name.endswith('.json'):
        file_path = f"{hdfs_directory}/{file_name}"
        print(f"processing {file_path}")
        with client.read(file_path) as file:
            for line in file:
                try:
                    tweet = json.loads(line)
                    tweet_p = {
                        '_id': tweet['id'],
                        'text': tweet.get('text'),
                        'timestamp_ms': tweet.get('timestamp_ms'),
                        'geo': tweet.get('geo'),
                        'coordinates': tweet.get('coordinates'),
                    }
                    if 'extended_tweet' in tweet:
                        tweet_p['full_text'] = tweet['extended_tweet'].get('full_text')

                    collection.update_one({'_id': tweet['id']}, {'$set': tweet_p}, upsert=True)
                except:
                    continue
