#!/usr/bin/env python
# coding: utf-8

# In[1]:
import warnings
import logging
import os
import requests
import zipfile
import tarfile
import bz2
import json
import shutil
from datetime import datetime
from hdfs import InsecureClient

# INIT VARIABLES
warnings.filterwarnings("ignore")
hdfs_directory = 'hdfs://hadoop-vm.internal.cloudapp.net:9000/twitter'
now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d%H%M%S")
logging.basicConfig(filename=f'extract-{date_time}.log', level=logging.DEBUG)


keywords = ['COVID-19', 'Coronavirus', 'Pandemic', 'Vaccine', 'Vaccination', 'Immunization', 'COVID vaccine', 'Vaccine rollout', 'Vaccine hesitancy', 'Vaccine mandate', 'Booster shot', 'Vaccine passport', 'Vaccination rate', 'Public health']
keywords_laboratories = ['Moderna', 'Pfizer', 'AstraZeneca', 'Johnson & Johnson', 'Sinovac', 'Sinopharm', 'Novavax', 'Sanofi', 'GlaxoSmithKline', 'BioNTech']
unique_keywords = list(set(keywords + keywords_laboratories))

hashtags = ['#COVID19', '#Coronavirus', '#Pandemic', '#Vaccine', '#Vaccination', '#GetVaccinated', '#COVIDVaccine', '#Immunization', '#VaccineHesitancy', '#VaccineMandate', '#BoosterShot', '#VaccinePassport', '#PublicHealth', '#StaySafe', '#VaccineRollout', '#VaccineTrials', '#ClinicalTrials', '#VaccineDevelopment', '#VaccineResearch', '#VaccineProduction', '#VaccineDistribution', '#VaccineSupplyChain', '#VaccineManufacturing', '#VaccineStorage', '#VaccineEfficacy', '#VaccineSafety', '#AntibodyTests', '#DiagnosticTests', '#PCRTests', '#SerologyTests', '#Immunology', '#HerdImmunity', '#VaccineNationalism']

hashtags_laboratories = ['#Moderna', '#Pfizer', '#BioNTech', '#AstraZeneca', '#JohnsonAndJohnson', '#Janssen', '#Novavax', '#Sinovac', '#Sinopharm', '#Sanofi', '#GSK']
unique_hashtags = list(set(hashtags + hashtags_laboratories))

# FUNCTIONS
def extract_zip_file(file_path, destination_folder):
    with zipfile.ZipFile(file_path,"r") as zip_ref:
        zip_ref.extractall(destination_folder)
        
def extract_tar_file(file_path, destination_folder):
    with tarfile.open(file_path, 'r') as tar:
        tar.extractall(path=destination_folder)
        
def extract_bz2_file(file_path, destination_folder):
    extracted_file_path = ""
    with bz2.open(file_path, 'rt') as f_in:
        file_name = os.path.basename(file_path).replace('.bz2', '')
        extracted_file_path = os.path.join(destination_folder, file_name)
        
        with open(extracted_file_path, 'w') as f_out:
            f_out.write(f_in.read())
            
    return extracted_file_path

def get_all_files(directory, recursive = False):
    file_list = []
    for root, dirs, files in os.walk(directory):
        if(recursive):
            for d in dirs:
                file_list = file_list + get_all_files(d,recursive)
        
        #files
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def create_folder(folder):
    try:
        os.mkdir(folder)
    except:
        pass

def LOG_INFO(message):
    logging.info(message)
    print(message)

# Extract files
output_dir = "data-01/output"
tweets_dir = "data-01/tweets"

# Prepare output folders
create_folder(tweets_dir)
create_folder(output_dir)

# Files process in previous run
error_files = ["data/twitter_stream_2020_01_14.tar"] # Check them later or download again

processed_files = ["data/twitter_stream_2020_01_01.tar",
        "data/twitter_stream_2020_01_02.tar",
        "data/twitter_stream_2020_03_16.tar",
        "data/twitter_stream_2020_01_04.tar",
        "data/twitter_stream_2020_01_05.tar",
        "data/twitter_stream_2020_01_06.tar",
        "data/twitter_stream_2020_01_07.tar",
        "data/twitter_stream_2020_01_08.tar",
        "data/twitter_stream_2020_01_09.tar",
        "data/twitter_stream_2020_01_10.tar",
        "data/twitter_stream_2020_01_11.tar",
        "data/twitter_stream_2020_01_12.tar",
        "data/twitter_stream_2020_01_13.tar"]

idx = 0
for data_folder in ["data","data-01"]:
    for file in get_all_files(data_folder):
        if("twitter" in file):
            
            # skip files processed
            if((file in processed_files) or (file in error_files)):
                logging.debug(f"Skipping file {file}")
                continue
                
            create_folder(output_dir)
            
            # Extract file
            try:
                LOG_INFO(f"Extracting {file}")
                if("zip" in file):
                    extract_zip_file(file, output_dir)
                else:
                    extract_tar_file(file, output_dir)
            except Exception as err:
                logging.exception('Exception: {0}'.format(err))
                continue
            
            
            LOG_INFO(f"Processing extracted files")
            idx+=1
            output_file = f"{tweets_dir}/covid-tweets-{date_time}-{idx}.json"
            # Open final file to save tweets on zip
            with open(output_file, 'x') as f_out:               
                for file in get_all_files(output_dir, recursive=True):
                    if file.endswith('.bz2'):
                        extracted_file_path = extract_bz2_file(file, tweets_dir)
                        # Read the file
                        with open(extracted_file_path, 'r') as f_in:
                            for line in f_in:
                                tweet = json.loads(line)
                                # Check if tweet contains a keyword or hashtag
                                try:
                                    # Get full tweet text when posible
                                    t_text = tweet['text']
                                    try:
                                        t_text = tweet['extended_tweet']['full_text']
                                    except:
                                        pass
                                    
                                    if any(keyword in t_text for keyword in unique_keywords) or any(hashtag in t_text for hashtag in unique_hashtags):
                                        json.dump(tweet, f_out)
                                        f_out.write('\n')
                                except Exception as err:
                                    pass
                        # remove extracted file
                        os.remove(extracted_file_path)
            # clean up output
            shutil.rmtree(output_dir)      
            

