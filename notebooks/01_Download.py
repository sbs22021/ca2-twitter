#!/usr/bin/env python
# coding: utf-8

# In[1]:
import logging
import sys
import os
import requests
import tarfile
import bz2
import json
from hdfs import InsecureClient
import warnings
warnings.filterwarnings("ignore")
hdfs_directory = 'hdfs://hadoop-vm.internal.cloudapp.net:9000/twitter'

year = 2020
if(len(sys.argv) < 7):
    month_from = int(sys.argv[1])
    month_to = int(sys.argv[2])
    compress_type = sys.argv[3]
    spacer = sys.argv[4]
    outputDir = sys.argv[5]
else:
    year = int(sys.argv[1])
    month_from = int(sys.argv[2])
    month_to = int(sys.argv[3])
    compress_type = sys.argv[4]
    spacer = sys.argv[5]
    outputDir = sys.argv[6]
    

# In[4]:
keywords = ['COVID-19', 'Coronavirus', 'Pandemic', 'Vaccine', 'Vaccination', 'Immunization', 'COVID vaccine', 'Vaccine rollout', 'Vaccine hesitancy', 'Vaccine mandate', 'Booster shot', 'Vaccine passport', 'Vaccination rate', 'Public health', 'WHO', 'CDC']
hashtags = ['#COVID19', '#Coronavirus', '#Pandemic', '#Vaccine', '#Vaccination', '#GetVaccinated', '#COVIDVaccine', '#Immunization', '#VaccineHesitancy', '#VaccineMandate', '#BoosterShot', '#VaccinePassport', '#PublicHealth', '#StaySafe']


# In[5]:


def extract_tar_file(file_path, destination_folder):
    with tarfile.open(file_path, 'r') as tar:
        tar.extractall(path=destination_folder)
        
def extract_bz2_file(file_path, destination_folder):
    with bz2.open(file_path, 'rt') as f_in:
        file_name = os.path.basename(file_path).replace('.bz2', '')
        extracted_file_path = os.path.join(destination_folder, file_name)
        
        with open(extracted_file_path, 'w') as f_out:
            f_out.write(f_in.read())
            
    return extracted_file_path

def get_all_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


# In[6]:

# change directory to dowload folder
output_directory = "/home/rmsryu/notebooks/CA2/ca2-twitter/notebooks/data"
output_directory_01 = "/home/rmsryu/notebooks/CA2/ca2-twitter/notebooks/data-01"
os.chdir(output_directory)


# In[7]:


def download_twitter_data(year, month, day, compress_type = "tar", spacer = "-"):
    filename = f"twitter{spacer}stream{spacer}{year}{spacer}{str(month).zfill(2)}{spacer}{str(day).zfill(2)}.{compress_type}"
    
    # Check file in both disk
    os.chdir(output_directory)
    if os.path.exists(filename):
        print(f"Downloaded: {filename}")
        return filename
    
    os.chdir(output_directory_01)
    if os.path.exists(filename):
        print(f"Downloaded: {filename}")
        return filename
    
    
    if(outputDir == "data"):
        os.chdir(output_directory)
    else:
        os.chdir(output_directory_01)
    
    url = f"https://archive.org/download/archiveteam-twitter-stream-{year}-{str(month).zfill(2)}/{filename}"
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {filename}")
        return filename
    else:
        print(f"Failed to download: {url}")


for month in range(month_from, month_to):
    for day in range(1, 32):
        try:
            download_twitter_data(year, month, day, compress_type, spacer)
        except Exception as e:
            print(f"Error downloading data for {year}-{month}-{day}: {e}")

