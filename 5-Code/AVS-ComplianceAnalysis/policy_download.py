#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#JA-
#Eunomia-2-on-the-fly privacy policy download.


# In[ ]:


#imports
import sys
import os
import codecs
import re
import spacy
import pickle
import json
import import_ipynb
import pyodbc
import requests
from bs4 import BeautifulSoup
import hashlib
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os.path
import shutil


# In[ ]:


conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=AVALON\SQLEXPRESS;'
                      'Database=AVSPrivacyCompliance;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()


# In[ ]:


#file containing skill information
skill_info = "skillinfo.txt"


# In[ ]:


def sha256_compute(file):
    hash_value = hashlib.sha256()
    #reading the file
    with open(file, 'rb') as fread:
        for block in iter(lambda: fread.read(4096), b""):
            hash_value.update(block)
    #return the hash value
    return hash_value.hexdigest()


# In[ ]:


def chromedriver_config():
    config = Options()
    config.add_argument("--headless")
    config.add_argument("--disable-gpu")
    config.add_argument("--no-sandbox")
    config.add_argument("--disable-dev-shm-usage")
    config.add_argument("--disable-extensions")
    config.add_argument("--disable-infobars")
    config.add_argument("--disable-browser-side-navigation")
    config.add_argument("--disable-blink-features=AutomationControlled")
    driver_file = Service(os.getcwd()+'\chromedriver.exe')
    return webdriver.Chrome(service=driver_file, options=config)


# In[ ]:


#wait until new skill is invoked, then read skill info from a file. 
def skill_information():
    while not os.path.exists(skill_info):
        time.sleep(1)
    
    while os.stat(skill_info).st_size == 0:
        time.sleep(1)

    with open(skill_info, "r", encoding="ISO-8859-1") as file:
        skill_name = file.readline().rstrip()
        ASIN = file.readline().rstrip()
        skill_id = file.readline().rstrip()
    
    previous_hash=sha256_compute(skill_info)
    print(previous_hash)
    return skill_name, ASIN, skill_id, previous_hash


# In[ ]:


while (True):
    
    #queries to select, update and delete records
    select_hash = "select policy_hash from skilldetails where skill_id =?"
    update_hash = "update skilldetails set policy_hash=? where skill_id =?"
    delete_tuples = "delete from PrivacyPolicyExtractRealTime where skill_id =?"

    skill_name, ASIN, skill_id, previous_hash = skill_information() #invoked skill's information
    skill_link="https://www.amazon.com/"+skill_name.replace(' ', '-')+"/dp/"+ASIN #url of the invoked skill
    
    #chrome driver to get the skill's link
    chromedriver = chromedriver_config()
    chromedriver.get(skill_link)
    element_policy_link=""

    try:
        #the privacy policy link element on skill's page
        element_policy_link = chromedriver.find_element(By.CSS_SELECTOR, '.laJguA .eka-DZO') 
    except Exception as e:
        element_policy_link = ""    

    #downloading privacy policy's content into a text file
    with open(f'../../privacypolicies/files/{skill_id}.txt', 'w') as f:
        print("Downloading privacy policy for the skill: ", skill_name)
        if element_policy_link!="":
            chromedriver.get(element_policy_link.get_attribute('href'))
            
            try:
                #if there are clickable items in the policy, wait for them and get their content
                clickables = ['expand', 'show more', 'toggle', 'view more', 'read more']
                for item in clickables:
                    expanding_items = chromedriver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{item}')]")
                    for entry in expanding_items:
                        try:
                            entry.click()
                            WebDriverWait(chromedriver, 2).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                        except Exception as e:
                            print(f"The item could not be clicked: {e}")
            finally:
                result = chromedriver.find_element(By.TAG_NAME, 'body').text
                f.write(result)
                   
        f.write('.')
        f.close()
    
    #copy the downloaded policy to another location for further processing
    shutil.copy(f'../../privacypolicies/files/{skill_id}.txt', f'../../privacypolicies/files/step2/{skill_id}.txt')
    #compute hash of the downloaded file
    recent_hash = sha256_compute(f'../../privacypolicies/files/{skill_id}.txt')
        
    #get the previously stored hash value
    cursor.execute(select_hash, (skill_id))
    prev_hash = cursor.fetchone()[0]
    
    print("New hash value is: ", recent_hash, "for the skill",skill_name)
    print("Previous hash value is: ", prev_hash, "for the skill",skill_name)
    
    if (recent_hash != prev_hash): #the policy file has been updated on the skill page.
        
        # delete the outdated policy records
        cursor.execute(delete_tuples, (skill_id))
        cursor.commit()
        
        with open(f'../../privacypolicies/records/record.txt', 'a') as rec:
            rec.write(f'../privacypolicies/files/{skill_id}.txt')
            rec.write('\r\n')
            rec.close()
            
        with open(f'../../privacypolicies/records/step2/record.txt', 'a+') as rec2:
            rec2.seek(0)
            body = rec2.read()
            if (body):  #checking if the file is not empty
                rec2.seek(0, os.SEEK_END)
                rec2.write('\n')
            rec2.write(f'../privacypolicies/files/step2/{skill_id}.txt')
            rec2.close()
        
        cursor.execute(update_hash, (recent_hash, skill_id))
        cursor.commit()
        print("Previous and new hash values do not match, creating record.txt file, and storing new hash value", skill_name)
    else:
        os.remove(f'../../privacypolicies/files/{skill_id}.txt')
        os.remove(f'../../privacypolicies/files/step2/{skill_id}.txt')
        print("Removing policy file because the previous and new hash values are same for skill", skill_name)

    while ((sha256_compute(skill_info))==previous_hash): # while there is no new skill invocation
        time.sleep(1)
    previous_hash=sha256_compute(skill_info);


# In[ ]:


#JA-
#Eunomia-2-on-the-fly privacy policy download.


# In[ ]:





# In[ ]:




