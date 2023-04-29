#!/usr/bin/env python
# coding: utf-8

# In[1]:


import warnings
warnings.filterwarnings("ignore")
hdfs_directory = 'hdfs://hadoop-vm.internal.cloudapp.net:9000/twitter'


# In[2]:


#pip install hdfs


# In[3]:


import os
import requests
import zipfile
import tarfile
import bz2
import json
import shutil
from hdfs import InsecureClient


# In[4]:


keywords = ['COVID-19', 'Coronavirus', 'Pandemic', 'Vaccine', 'Vaccination', 'Immunization', 'COVID vaccine', 'Vaccine rollout', 'Vaccine hesitancy', 'Vaccine mandate', 'Booster shot', 'Vaccine passport', 'Vaccination rate', 'Public health']
keywords_laboratories = ['Moderna', 'Pfizer', 'AstraZeneca', 'Johnson & Johnson', 'Sinovac', 'Sinopharm', 'Novavax', 'Sanofi', 'GlaxoSmithKline', 'BioNTech']
unique_keywords = list(set(keywords + keywords_laboratories))

hashtags = ['#COVID19', '#Coronavirus', '#Pandemic', '#Vaccine', '#Vaccination', '#GetVaccinated', '#COVIDVaccine', '#Immunization', '#VaccineHesitancy', '#VaccineMandate', '#BoosterShot', '#VaccinePassport', '#PublicHealth', '#StaySafe', '#VaccineRollout', '#VaccineTrials', '#ClinicalTrials', '#VaccineDevelopment', '#VaccineResearch', '#VaccineProduction', '#VaccineDistribution', '#VaccineSupplyChain', '#VaccineManufacturing', '#VaccineStorage', '#VaccineEfficacy', '#VaccineSafety', '#AntibodyTests', '#DiagnosticTests', '#PCRTests', '#SerologyTests', '#Immunology', '#HerdImmunity', '#VaccineNationalism']

hashtags_laboratories = ['#Moderna', '#Pfizer', '#BioNTech', '#AstraZeneca', '#JohnsonAndJohnson', '#Janssen', '#Novavax', '#Sinovac', '#Sinopharm', '#Sanofi', '#GSK']
unique_hashtags = list(set(hashtags + hashtags_laboratories))



# In[5]:


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


# In[ ]:


output_dir = "data-01/output"
tweets_dir = "data-01/tweets"

create_folder(tweets_dir)
create_folder(output_dir)

idx = 0
for data_folder in ["data","data-01"]:
    for file in get_all_files(data_folder):
        if("twitter" in file):
            create_folder(output_dir)
            
            # Extract file
            print(f"Extracting {file}")
            if("zip" in file):
                extract_zip_file(file, output_dir)
            else:
                extract_tar_file(file, output_dir)
            
            
            print(f"Processing extracted files")
            idx+=1
            output_file = f"{tweets_dir}/covid-tweets-{idx}.json"
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
                                except:
                                    pass
                        # remove extracted file
                        os.remove(extracted_file_path)
            # clean up output
            shutil.rmtree(output_dir)
            break         
            

