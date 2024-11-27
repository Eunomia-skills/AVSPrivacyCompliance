#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#JA-
#Eunomia-1-main code for compliance validation.


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
import os.path
import numpy as np
import string
import csv
import time
from unidecode import unidecode
import re
import subprocess
import torch


# In[ ]:


# files

src = "output.txt"
stop_msg = "response.txt"
warn_msg = "warn.txt"


# In[ ]:


conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=AVALON\SQLEXPRESS;'
                      'Database=AVSPrivacyCompliance;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()


# In[ ]:


subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_trf'], check=True)


# In[ ]:


nlp = spacy.load("en_core_web_trf", exclude=["ner"])
print(nlp.pipe_names)
nlp_entity = spacy.load("model-transformer")
nlp.add_pipe("ner", source=nlp_entity)
print(nlp.pipe_names)


# In[ ]:


remove_words=['your','may','to','ve', 'couldn', 'own', 'themselves', 'me', 'same', 'these', 'between', "it's", 
                  'being', 'below', "wasn't", 'some', 'very', 'further', 'don', 'at', 'why', 'been', 'won', 'an', 'him', 
                  'down', 'its', 'if', 'wasn', 'off', 's', 'ma', 'on', 'this', 'himself', 'can', 'until', 'was', 'for', 'my', 
                  'than', 'after', 'but', 'nor', 'are', "you've", "you'll", 'your', 'against', 'aren', 'during', 'as', 'doesn',
                  'through', 'you', 'into', "hadn't", 'they', 'from', "couldn't", 'wouldn', 'yourselves', 'ain', 'doing', 
                  'ourselves', 'will', "haven't", 'so', "weren't", 'up', "wouldn't", 'to', 'too', 'and', "you're", 'is', 'we',
                  'the', 'her', "didn't", "mightn't", "don't", "she's", 'weren', 'ours', "isn't", 'yours', 'such', 'now', 'in',
                  'does', 'his', 'it', 't', 'once', 'only', 'should', "hasn't", 'itself', 'more', 'no', 'about', 'that', 
                  "should've", 'mustn', 'with', 'out', "aren't", "won't", "you'd", 'when', 'do', 'yourself', 'shouldn', 
                  'isn', 'most', "needn't", 'myself', 'o', 'just', "shouldn't", 'theirs', 'herself', 'where', 'because', 
                  'them', 'had', 'while', 'be', 'again', 'did', 'she', 'both', 're', 'were', 'there', 'am', 'of', 'whom', 
                  'have', 'over', 'd', 'y', 'all', 'hadn', 'll', 'their', 'has', 'who', 'any', 'each', 'our', 'not', 'before', 
                  'how', 'mightn', "mustn't", 'shan', "that'll", 'under', 'or', 'hasn', 'haven', 'a', 'other', 'having', 
                  'those', 'hers', "doesn't", 'which', 'needn', 'he', 'few', 'm', 'by', 'didn', 'i', "shan't", 'above', 
                  'what', 'here', 'then','may','must','following','way','is', 'please']


# In[ ]:


def main():
    sensitive_practices, all_practices, text = readOutput() #invocation for skill practices from interactions
    
    skill_name,skill_id,ASIN,policy_practices = readPolicy()    #invocation for practice declarations from policies
  
    compliance_results = complianceCheck(sensitive_practices, policy_practices,skill_name,ASIN,skill_id,text) #invocation for compliance check

    save_results(compliance_results)


# In[ ]:


#skill practices from interactions

def readOutput():
    #These practices were generated automatically using the BERT model. Also, added to it few practices that SkillDetective provided
    practices = ['Address','addresses', 'Name', 'Email', 'Birthday', 'Age', 'Gender', 'Location',
'Phonebook', 'phone', 'Profession', 'Income', 'Zipcode', 'Postal code', 'Passport number', 'Driver license number','Driver license', 'Bank account number', 'Debit card number', 'Credit card number', 'SSN',
'Height', 'Weight', 'Blood group', 'Blood pressure', 'Blood glucose', 'Blood Oxygen', 'Heart rate', 'Body temperature', 'Sleep data', 'Fat percentage',
'Mass index', 'Waist circumference', 'Menstruation', 'Period','pregnancy','medication','pill',
'Name', 'Address', 'SSN', 'Email address',
'Internet protocol address', 'Age', 'Gender', 'Birthday', 'Medical record number', 'Health plan beneficiary number', 'Driver license number', 'ethnicity', 
'affiliation', 'orientation', 'zip code', 'first name', 'last name', 'full name',
'social security number', 'bank account number','email address','account user info','phone','address','account details',
'photo','health and wellness','social media information','geographical location','payment',
'organization info','motion','weather','calendar','camera','sim serial number','text message',
'browser information','operating system','usage information','ip address','ip','payment card information',
'date of birth','address','network information','internet service provider','advertising id',
'android id','imei','device identifier','payment method','ssn','payment card expiration date','purchase date','purchase amount',
'travel information','vehicle information','salary','vehicle identification number','fitness activity information',
'employment information','body weight','operating system','browser information','browser history','browser type',
'device setting','device type','business information','email address','website address','mac address',
'government-issue identification information','education level','date of birth','birth year',
'bank routing number','educational information','ip address','contact information','security code','physical traits',
'social media account credential','social media friends','social media profile url','social media username',
'social media account information','social media information','browsing behavior','browser information',
'vehicle usage information','employer name','business name','photo','race','gender','school','phone tower','biography',
'profile information','isp','internet service provider','insurance coverage information','medical insurance information',
'insurance history','insurance carrier','insurance policy number','state','city','zip code','country','registration information',
'membership information','password','internet browse history','lifestyle information','facebook profile information',
'credit history','blood glucose level','heart rate','call log','education information','interaction information',
'philosophical belief','relationship status','political view','activity information','usage information','purchase information',
'shopping habits','biometric information','genetic information','payment card information','payment card number',
'payment information','text message','disability','allergy','credit score','shipping information','account balance information',
'operating system','photo metadata','operating system version','body mass index','credit card security code',
'identifier','blood pressure','emergency contact information','contact information','postal address','address',
'transaction information','financial transaction information','accelerometer information','device information',
'prescription information','geocaching log','account information','credit information','license number',
'financial account information','bank account number','driver license information','driver license number',
'vehicle license number','username','serial number','address book','health and wellness','person age','network information',
'traffic information','log information','demographic information','person name','contact name','sexual orientation',
'sexual history','user information','gps','geographical location','weather','phone','calendar','payment','camera',
'account user info','account details','sim serial number','gallery','zodiac','sit-up','situp','plank','workout','work out',
'pushup','exercise','timezone','steps','pedometer','street name','street number','bithday']

    practices_dict= {
"how old are you": 'age', 
"when were you born": 'age',
"what is your date of birth": 'age',
"say your date of birth": 'age',
"what is your year of birth": 'age',
"what year did you come into this world": 'age',
"how many birthdays have you celebrated so far": 'age',
"when did you start your life journey": 'age',
"what is your birth year": 'age',
"how many years have you been alive": 'age',
"what year did you first see the light of day": 'age',
"when did you begin your time on Earth": 'age',
"how long have you been with us": 'age',
"When did you start growing up": 'age',
"can you please confirm that you are aged": 'age',
"specify the child's age": 'age',
"where do you live":'location' ,
"What's the city?":'city',
"where are you from": 'location',
"where are you located": 'location',
"Where is your current residence": 'location',
"What is the address of your home": 'location',
"In which part of the city do you stay": 'location',
"What is your locality": 'location',
"Where do you call your hometown": 'location',
"What is the name of the place you reside": 'location',
"What area are you living in": 'location',
"What is the district you live in": 'location',
"Where can you be found": 'location',
"What is the region you currently occupy": 'location',
"what can i call you": 'name', 
"What should I address you as": 'name',
"How may I refer to you": 'name',
"What is your given name": 'name',
"By what title do you go by": 'name',
"What is the name you prefer to be called": 'name',
"What is your appellation": 'name',
"What may I call you": 'name',
"may i get your name": 'name',
"start by getting your first name": 'name',
"can we know your first name": 'name',
"How should I name you": 'name',
"What is the word to identify you": 'name',
"What do you like to be called": 'name',
"to add a name, say": 'name',
"we would like your name": 'name',
"male or female": 'gender',
"you a man or woman": 'gender',
"you a man or a woman": 'gender',
"if you are a man or a woman": 'gender',
"How do you identify yourself": 'gender',
"What gender do you relate to": 'gender',
"Which group do you consider yourself a part of": 'gender',
"What is your gender identity": 'gender',
"What category do you place yourself under": 'gender',
"What is your gender expression": 'gender',
"How do you describe your gender": 'gender',
"What gender do you perceive yourself as": 'gender',
"What is your gender orientation": 'gender',
"Which gender do you see yourself as": 'gender',
"what to call you":'name',
"where are you starting from":'location',
"where you're heading at":'location',
"where are you going":'location',
"where you are heading at":'location',
"where do you wish to fly":'location',
"which station do you board":'location',
"which city are you planning to visit":'city',
"which state are you planning to purchase a home":'state',
"calculate your savings":'payment',
"tell me the dollar amount":'payment',
"problem with your payment method":'payment',
"tell us your due date":'pregnancy',
"prepare yourself for a 5 minutes plank workout":'fitness activity information',
"begin exercises right away":'fitness activity information',
"guide you through the steps to create a routine":'fitness activity information',
"repeat this stretch":'fitness activity information',
"how much do you earn":'income',
"who would you like to sing happy birthday to": 'name'
}

    questions=['answer','grant','add','start','accept','added','tell','grant','granted','provide','ensure','include','enter','mention','give me','link me','were','who','whose','whos','what','what''s','whats','whatas','when','where','why','how','which','do','does','can',
               'could','will','would','should','need','needs','required','requires','ask','asked','asks','access','say','add','set','store','storing','enable','may', 'report','choose','turn on','monitor','track','are you']
    direct_questions=['who','whose','whos','what','what''s','whats','whatas','when','where','why','how','which','could','would','should','are you','will']
    all_practices=[]
    sensitive_practices=[]
    person_related=['your','you','someone','someone''s','someones','some','who','who''s','whose','recipient','default','permission','permissions','access','lady','our']
        
    questions_pattern = re.compile(r'\b(' + '|'.join(questions) + r')\b')
    person_related_pattern = re.compile(r'\b(' + '|'.join(person_related) + r')\b')
    practices_lower = [practice.lower() for practice in practices]
    practices_pattern = re.compile(r'\b(' + '|'.join(practices_lower) + r')\b')
    direct_questions_pattern = re.compile(r'\b(' + '|'.join(direct_questions) + r')\b')

    i=0;
    while (i==0):
        while not os.path.exists(src):
            time.sleep(1)
    
        while os.stat(src).st_size == 0:
            time.sleep(1)
        
        with open(src, 'r',encoding="ISO-8859-1") as f: #read skill output from a text file
            text = f.read()
            text = unidecode(text) #replacing non-ascii with ascii equivalents
        f.close()
        os.remove(src) #delete the text file, will be created again for the new output
        
        isinformation = False
        sentences = re.split(r'(?<=[a-zA-Z0-9].[\n\.?!]) +(?=[a-zA-Z0-9])', text) #need to handle multiple sentences from skill output
        for sent in sentences:
            if sent.find("?") == -1 and direct_questions_pattern.search(sent.lower()) and 'when linking your account' not in sent.lower():#it is just info if direct question pattern is there but does not end with a ?
                isinformation = True
            #but what if all the sentence-end symbols are missing? Then it could be a question.
            if sent.find("?") == -1 and sent.find(".") == -1 and sent.find("!") == -1 and sent.find(":") == -1 and sent.find(";") == -1:
                isinformation=False
            #what if the sentence contains both tell from questions and direct question words. It will be missing a ? but would still be a question.
            #e.g.; tell me how much ... etc.
            if isinformation == True and 'tell ' in sent.lower():
                isinformation = False
            if isinformation == True and 'report ' in sent.lower():
                isinformation = False
            if isinformation == True and 'say ' in sent.lower():
                isinformation = False
            if isinformation == True and 'need ' in sent.lower():
                isinformation = False
            if isinformation == True and 'mention ' in sent.lower():
                isinformation = False
            if isinformation == True and 'give me ' in sent.lower():
                isinformation = False
            if isinformation == True and 'link me ' in sent.lower():
                isinformation = False

                
            #what if the sentence contains 'you can say', then it is an instruction rather than Alexa asking a question
            #e.g.; you can say, what is your name? then the question is to be asked by the user, not Alexa.
            #also, 'Do you want more' indicates information from Alexa
            print("isinformation: ",isinformation)
            if 'you can say' in sent.lower() or 'you can not say' in sent.lower() or 'you can just say' in sent.lower() or 'you can also say' in sent.lower() or 'just say' in sent.lower() or 'try saying' in sent.lower() or 'you can choose' in sent.lower() or 'you can search' in sent.lower() or 'you can contact' in sent.lower() or 'you can expect' in sent.lower() or 'you can email us' in sent.lower() or 'you can ask' in sent.lower() or 'you can start by asking' in sent.lower() or 'things you need to remember' in sent.lower() or 'you can also do' in sent.lower() or 'gender of your character' in sent.lower() or 'you can look for' in sent.lower() or 'you can check' in sent.lower() or 'you can also ask' in sent.lower() or ' you can verify' in sent.lower() or 'ask me' in sent.lower() or 'do you want more' in sent.lower()  or 'for which you would like to know' in sent.lower() or 'would you like to' in sent.lower() or 'would you like me to' in sent.lower() or 'would you like another' in sent.lower() or 'do you want to know' in sent.lower() or 'youd like to' in sent.lower() or 'you''d like to' in sent.lower()  or 'like to receive this' in sent.lower() or 'you would like to' in sent.lower() or 'we can tell' in sent.lower() or 'i can tell' in sent.lower() or 'i can also tell' in sent.lower() or 'i can provide' in sent.lower() or 'i can help you' in sent.lower() or 'this skill will help you' in sent.lower() or 'say add or delete' in sent.lower() or 'do you mean' in sent.lower() or 'here is your fact' in sent.lower() or 'here''s your fact' in sent.lower() or 'your fact' in sent.lower() or 'atlas' in sent.lower() or 'computers insisted on a blood work report for bank account creation' in sent.lower() or 'computer would reply that it did not trust' in sent.lower() or 'try asking' in sent.lower() or 'seniors who have a disability' in sent.lower() or 'some may claim' in sent.lower() or 'scammer' in sent.lower() or 'your name will be' in sent.lower() or 'you will find your' in sent.lower() or 'next hint' in sent.lower() or 'contact us' in sent.lower() or 'we will contact you' in sent.lower() or 'please contact' in sent.lower() or 'ask us to contact' in sent.lower() or 'declutter your mind' in sent.lower() or 'i''ve added' in sent.lower() or 'ive added' in sent.lower() or 'do you mean' in sent.lower() or 'specify wether you want' in sent.lower() or 'i see you''ve used' in sent.lower() or 'i see youve used' in sent.lower() or 'is in your flash briefing' in sent.lower() or 'i can generate' in sent.lower() or 'i can give' in sent.lower() or 'i read' in sent.lower() or 'i will read' in sent.lower() or 'i will provide' in sent.lower() or 'i have added' in sent.lower() or 'i will tell' in sent.lower() or 'having trouble accessing' in sent.lower() or 'this skill helps' in sent.lower() or 'welcome to' in sent.lower() or 'you can know' in sent.lower() or 'will never ask for' in sent.lower() or 'is available with' in sent.lower() or 'do you mean' in sent.lower() or 'this is the story of' in sent.lower() or 'let me tell you' in sent.lower() or 'would you like me to' in sent.lower() or 'would you like the' in sent.lower() or 'its features include' in sent.lower() or 'you have been putting off' in sent.lower() or 'phishing emails request' in sent.lower() or 'not to be trusted' in sent.lower() or 'complained that' in sent.lower() or 'you will find your' in sent.lower() or 'hurt me so good' in sent.lower() or 'under cases of' in sent.lower() or 'to address the' in sent.lower() or 'send them an email' in sent.lower() or 'any email that you send' in sent.lower() or 'say remind me' in sent.lower() or 'your tip' in sent.lower() or 'hear some more' in sent.lower() or 'want some more' in sent.lower() or 'you want another' in sent.lower() or 'my name is' in sent.lower() or 'your flash briefing' in sent.lower() or 'did you know' in sent.lower() or 'visit our latest' in sent.lower() or 'ask for information' in sent.lower() or 'i can help you' in sent.lower() or 'do you need' in sent.lower() or 'you can also email us' in sent.lower() or 'welcome to email marketing' in sent.lower() or 'email is dead' in sent.lower() or 'i can answer' in sent.lower() or 'you can do it all' in sent.lower() or 'diversify your income' in sent.lower() or 'for business coaching' in sent.lower() or 'for contact infromation' in sent.lower() or 'yo mama so old' in sent.lower() or 'have a habit of exercising' in sent.lower() or 'habit of using some' in sent.lower() or 'it will help to make you' in sent.lower() or 'checking your phone during conversations' in sent.lower() or 'phones can easily get control' in sent.lower() or 'phone habits' in sent.lower() or 'are you interested to find out' in sent.lower() or 'you can ask me' in sent.lower() or 'you can also send a message' in sent.lower() or 'shuffled letters of an animal' in sent.lower() or 'you can ask questions' in sent.lower() or 'you can ask me things' in sent.lower() or 'by getting your heart rate up' in sent.lower() or 'your health tip for today' in sent.lower() or 'can have an effect on your weight and blood glucose' in sent.lower() or 'menopause is diagnosed after' in sent.lower() or 'seemingly harmless common medications' in sent.lower() or 'you can schedule a consultation' in sent.lower() or 'track your weight on regular basis' in sent.lower() or 'you can say' in sent.lower() or 'would you like to represent' in sent.lower() or 'they can do research' in sent.lower() or 'you can celebrate' in sent.lower() or 'check the page likes and description' in sent.lower() or 'twitter trending topics' in sent.lower() or 'need more experience' in sent.lower() or 'versions of each name' in sent.lower() or 'meaning behind your' in sent.lower() or 'create something beautiful' in sent.lower() or 'you can now choose' in sent.lower() or "here's the list" in sent.lower() or 'here the list' in sent.lower() or 'heres the list' in sent.lower() or 'say next' in sent.lower() or 'say no' in sent.lower() or 'add some states' in sent.lower() or 'would you like the menu' in sent.lower() or 'recommended items for your emergency' in sent.lower() or 'you want to lookup' in sent.lower() or 'say my name' in sent.lower() or 'get pranked' in sent.lower() or 'the entire galaxy' in sent.lower() or 'high blood pressure can lead to' in sent.lower() or 'keep your weight in check' in sent.lower() or 'someone is impertinent' in sent.lower() or 'highly productive people' in sent.lower() or 'lower your tax bill' in sent.lower() or 'romeo and juliet' in sent.lower() or 'does not discriminate' in sent.lower() or 'name of your pet' in sent.lower() or 'list of all the recipes' in sent.lower() or 'would you like details' in sent.lower() or 'your joke' in sent.lower() or 'i can answer common questions' in sent.lower() or 'watch for symptoms' in sent.lower() or 'you can find contact information' in sent.lower() or 'or say help' in sent.lower() or 'find the recipe you want' in sent.lower() or 'say multiplication' in sent.lower() or 'say case one' in sent.lower() or 'you want a substitution' in sent.lower() or 'a parent needs to give permission only once' in sent.lower() or 'i invite you to contact the' in sent.lower() or 'as outlined by stanford' in sent.lower():
                isinformation = True

            if isinformation == True and 'please select ' in sent.lower():
                isinformation = False
            if isinformation == True and 'what city and state would you like to' in sent.lower():
                isinformation = False                
            if isinformation == True and 'just say give me a exercise' in sent.lower():
                isinformation = False                             
            if isinformation == True and 'what kind of workout' in sent.lower():
                isinformation = False                
            if isinformation == True and 'how many workouts you have logged' in sent.lower():
                isinformation = False                
            if isinformation == True and 'just say give me a exercise' in sent.lower():
                isinformation = False                
            if isinformation == True and 'tell you how many workouts' in sent.lower():
                isinformation = False                
            if isinformation == True and "today's workout" in sent.lower():
                isinformation = False                
            if isinformation == True and "todays workout" in sent.lower():
                isinformation = False     
            if isinformation == True and "check your progress" in sent.lower():
                isinformation = False      
            if isinformation == True and "please enable full name" in sent.lower():
                isinformation = False      
            if isinformation == True and "exercise" in sent.lower():
                isinformation = False
            if isinformation == True and "workout" in sent.lower():
                isinformation = False
            if isinformation == True and "say the last name of the person" in sent.lower():
                isinformation = False
            if isinformation == True and "say your zip code" in sent.lower():
                isinformation = False
            if isinformation == True and "your first name" in sent.lower():
                isinformation = False
            if isinformation == True and "ask your name" in sent.lower():
                isinformation = False
            if isinformation == True and "what's your name" in sent.lower():
                isinformation = False

            if isinformation == True and "weather for your location" in sent.lower():
                isinformation = False
            if isinformation == True and "send a link to your phone" in sent.lower():
                isinformation = False
            if isinformation == True and "submit a phone number" in sent.lower():
                isinformation = False

            if isinformation == True and "need your age" in sent.lower():
                isinformation = False
            if isinformation == True and "know your weight" in sent.lower():
                isinformation = False
            if isinformation == True and "what address" in sent.lower():
                isinformation = False
            if isinformation == True and "retrieve weather data" in sent.lower():
                isinformation = False

            if isinformation == True and "exercise challenge" in sent.lower():
                isinformation = False                
            if isinformation == True and "how you want to work out" in sent.lower():
                isinformation = False   
            if isinformation == True and "weight loss tips" in sent.lower():
                isinformation = False                
            if isinformation == True and "say the name of" in sent.lower():
                isinformation = False                
            if isinformation == True and "say your phone number" in sent.lower():
                isinformation = False                
            if isinformation == True and "say your first and last name" in sent.lower():
                isinformation = False                
            if isinformation == True and "tell me the name" in sent.lower():
                isinformation = False                
            if isinformation == True and "name each grandchild" in sent.lower():
                isinformation = False                
            if isinformation == True and "permissions to access your" in sent.lower():
                isinformation = False                
            if isinformation == True and "give me permission to view your" in sent.lower():
                isinformation = False                
            if isinformation == True and "allow alexa to access your" in sent.lower():
                isinformation = False                
            if isinformation == True and "what name would you like" in sent.lower():
                isinformation = False                
            if isinformation == True and "start by telling me" in sent.lower():
                isinformation = False                

            if isinformation == True and "for example: zip code" in sent.lower():
                isinformation = False                
            if isinformation == True and "tell you where to ride" in sent.lower():
                isinformation = False                
            if isinformation == True and "which city would you like to depart" in sent.lower():
                isinformation = False                
            if isinformation == True and "tell me your country" in sent.lower():
                isinformation = False                
            if isinformation == True and "location and remind you" in sent.lower():
                isinformation = False                
            if isinformation == True and "which zip code would you like" in sent.lower():
                isinformation = False                
            if isinformation == True and "tell me your name" in sent.lower():
                isinformation = False          
            if isinformation == True and "like to know your preferred name" in sent.lower():
                isinformation = False                
            if isinformation == True and "know your first name" in sent.lower():
                isinformation = False  
            if isinformation == True and "first name please" in sent.lower():
                isinformation = False                
            if isinformation == True and "you would like to work hard" in sent.lower():
                isinformation = False                
            if isinformation == True and "gain access to your" in sent.lower():
                isinformation = False           
            if isinformation == True and "grant access to your" in sent.lower():
                isinformation = False                

            if isinformation == True and "city you choose" in sent.lower():
                isinformation = False                
            if isinformation == True and "what is your name" in sent.lower():
                isinformation = False                
            if isinformation == True and "give me your human name" in sent.lower():
                isinformation = False                
            if isinformation == True and "tell your blood group" in sent.lower():
                isinformation = False                
            if isinformation == True and "followed by an email address" in sent.lower():
                isinformation = False                
            if isinformation == True and "used city of" in sent.lower():
                isinformation = False                
            if isinformation == True and "which state would you like to" in sent.lower():
                isinformation = False                
            if isinformation == True and "zip code of your city" in sent.lower():
                isinformation = False                
            if isinformation == True and "city weather" in sent.lower():
                isinformation = False       
            if isinformation == True and "weather of your city" in sent.lower():
                isinformation = False                
            if isinformation == True and "saved names" in sent.lower():
                isinformation = False                
            if isinformation == True and "save names" in sent.lower():
                isinformation = False                
            if isinformation == True and "perform an exercise" in sent.lower():
                isinformation = False                
            if isinformation == True and "say your phone number" in sent.lower():
                isinformation = False                
            if isinformation == True and "accept the address permission" in sent.lower():
                isinformation = False                
            if isinformation == True and "like to know your name" in sent.lower():
                isinformation = False                
            if isinformation == True and "create the right workout for you" in sent.lower():
                isinformation = False                
            if isinformation == True and "what phone number" in sent.lower():
                isinformation = False                
            if isinformation == True and 'please answer ' in sent.lower():
                isinformation = False                
            if isinformation == True and 'please say ' in sent.lower():
                isinformation = False                
            if isinformation == False and 'you can' in sent.lower() and 'get your' in sent.lower():
                isinformation = True                
            if isinformation == False and 'some of the' in sent.lower() and 'services are' in sent.lower():
                isinformation = True                
                
                
            sent_lower=sent.lower()
            
            #removing strings where the question is not meant for the user, but just to inform the user to ask this from VA
            sent_lower=sent_lower.replace("'where are you located", '').replace('"where are you located?"','').replace("here's male or female",'').replace('google male or female','')
            if "you can ask me things" in sent_lower and isinformation == True:
                sent_lower=sent_lower.replace('where are you located', '')
            
            #match the sentences with practices_dict. If matched, store the practice in the list
            for prac in practices_dict:
                prac_lower=prac.lower()
                if prac_lower.translate(str.maketrans('', '', string.punctuation)) in sent_lower.translate(str.maketrans('', '', string.punctuation)):
                    sensitive_practices.append(practices_dict[prac])
            
            #check the structure, is it asking for a question etc? is your/you in sentence? contains '?' and not just information
            #if any(word in sent_lower for word in questions) and any(wrd in sent_lower for wrd in person_related):
            if questions_pattern.search(sent_lower) and person_related_pattern.search(sent_lower) and isinformation==False:    
                
                #remove the unnecessary parts, clean up the data, then extract the data objs
                #state fair not to be confused with state, email address not with address etc. Exceptions are:
                if "name" in sent_lower and "medication" in sent_lower:
                    sent_lower=sent_lower.replace('name', '')
                if "name" in sent_lower and "services" in sent_lower and "access to your name" not in sent_lower:
                    sent_lower=sent_lower.replace('name', '')                    
                if "ingredient" in sent_lower and "weight" in sent_lower:
                    sent_lower=sent_lower.replace('weight', '')     
                if "bus" in sent_lower and "stop" in sent_lower:
                    sent_lower=sent_lower.replace('stop', 'location')   
                #if a skills talks about completing a short exercise, it is not talking about physical exercise
                if "short exercise" in sent_lower:
                    sent_lower=sent_lower.replace('exercise', '')
                #if the skill provides information where a university is located, it is not asking for personal information    
                if "university" in sent_lower and "is located in" in sent_lower:
                    sent_lower=sent_lower.replace('country', '').replace('city', '')                       
                #if a skill wishes happy birthday, it is not asking about the birthday
                if "birthday" in sent_lower:
                    if "may" in sent_lower or "happy" in sent_lower:
                        sent_lower=sent_lower.replace('birthday', '')
                #if a skill quotes a verse, it is not really asking for personal info
                if "to your old age and gray hairs" in sent_lower or "age does not" in sent_lower or "you from age" in sent_lower or "i have given you my name" in sent_lower or "name for" in sent_lower or "in your name" in sent_lower:
                    sent_lower=sent_lower.replace('age', '').replace('name', '')
                
                sent_lower=sent_lower.replace('state fair', '').replace('state married', '').replace('washington state', '').replace('leave the state', '').replace('state university', '').replace('missed school','').replace('she was in school','').replace('ready for school','').replace('at school','').replace('in high school','').replace('westwood elementary school','').replace('booksher middle school','').replace('santa clara high school','').replace('school bus','').replace('state school','').replace('state journal','').replace('weight a pie','').replace('his own body weight','').replace('we lose some weight','').replace('current block height','').replace('your weight not your phone','').replace('calendar day','')
                sent_lower=sent_lower.replace('school district', 'location').replace('mac address', 'location').replace('hostel in a location','').replace('device address', 'location').replace("device's address", 'location').replace('devices address', 'location').replace('region name', 'location').replace('street number and name','address').replace('street number','address').replace('street name','address').replace('city name','city').replace('attractions in the city','').replace('oldest city in the world','').replace('city treasures','').replace('the city is home to','').replace('exploring the city','' ).replace('name of your city','city').replace('name of the city','city').replace('state name','state').replace('country name','country').replace('country club','').replace('which country is the','').replace('country in which','').replace('city in which country','').replace('in which country','').replace('in which city','').replace('in which state','').replace('violence of the state','').replace('in which indian city','').replace('originated from which country','').replace('country capital','').replace('country austria','').replace('school uniform','').replace('grammar school','').replace('my norfolk city services','my norfolk').replace('redwood city','').replace('new york city','').replace('chennai city','').replace('city popular with','').replace('city is quite','').replace('affordable in the city','').replace('cheap ones in the city','').replace('State of the market','')
                sent_lower=sent_lower.replace('email address', 'email')
                sent_lower=sent_lower.replace('ip address', 'location').replace('synonym of location','')
                sent_lower=sent_lower.replace('full name', 'name').replace('how to address you','name').replace('category name', '').replace('name of character', '').replace('say my name', '').replace('name registry', '').replace('scheme name', '').replace('name of rama','').replace('interval name','').replace('pick a name','').replace('name given to me','').replace('name the language','').replace('landers name','').replace('name the characters','').replace('name the robot','').replace('pirate name','').replace('forgot your name','').replace('name from the captain','').replace('set your username', '').replace('name for your cat', '').replace('name of the stream','').replace('original name','').replace('originally named','').replace('station name', '').replace('name of a station', '').replace('celebrity name', '').replace('name of a plant', '').replace('avataar name', '').replace('carrier name', '').replace('if you say his name','').replace('list name', '').replace('giant name', '').replace('name of flight', '').replace('in its name', '').replace('last name', 'name').replace('first name', 'name').replace('first and last name', 'name').replace('names','name').replace('movie name','').replace('airline name','').replace('name of the quote','').replace('name of the business','').replace('business name','').replace('recipes by name','').replace('name of a stream','').replace('program name','').replace('programs name','').replace('domain name','').replace('company name','').replace('book name','').replace('class name','').replace('boat name','')
                sent_lower=sent_lower.replace('race calendar', '').replace('5k race', 'fitness activity information').replace('calendar briefing', '').replace('race result','').replace('human race','').replace('win the race','').replace('new race','').replace('want to race','').replace('horse race','').replace('race day','').replace('in a race','')
                sent_lower=sent_lower.replace('nickname', '').replace('nick name','').replace('name of the watch','').replace('name of the event','').replace('name of the destination','').replace('state nick','').replace('natural state','').replace('name of an animal','').replace('artist name','').replace('guess another name','').replace('option name','').replace('name of your favorite footballer','').replace('the name of the clock','').replace('name of the prayer','').replace('store name','').replace('name of a monster','').replace('name of the monster','').replace('name of your favorite artist','').replace('name of the singer','').replace('name of your network','').replace('name Jacob','').replace('name is Benjamin','').replace('scammers may use a name','').replace('pokemon''s name','').replace('player name','').replace('animal name','').replace('in my name','').replace('atlantic city electric','').replace('your pickup city is','').replace('your drop off city is','')
                sent_lower=sent_lower.replace('contact lense', '').replace('for us to contact you','').replace('app on your phone','').replace('the phone number is','').replace('the phone is','').replace('unlock the phone','').replace('on the phone with','').replace('number to get in contact','phone').replace('phone with no service','')
                sent_lower=sent_lower.replace('simple email service', '').replace('email campaigns', '').replace('subject line of an email','').replace('size of your email','').replace('emails with high clickthrough','').replace('email designs', '').replace('emails per day', '').replace('email nurture campaigns', '').replace('email sending and receiving service','').replace('email sending service','').replace('email receiving service','').replace('review the email','').replace('please email','').replace('send us an email','').replace('if you receive an email','').replace('you can send email','')
                sent_lower=sent_lower.replace('zodiac', 'birthday').replace('bithday','birthday')
                sent_lower=sent_lower.replace('installation steps', '').replace('workout pants','').replace('health tip','').replace('school alexa skill','').replace('everyone of every age','').replace('launch gallery','').replace('location of a cooking ingredient','').replace('phone every now and then','').replace('check your phone','').replace('look at their phones','').replace('phone habits','').replace('guess your age','').replace('re age is','').replace('movie name', '').replace('tv show name', '').replace('tv series name', '').replace('tv servies name', '').replace('parts of the country', '').replace('first step', '').replace('step out today', '').replace('name of the technique', '').replace('weight so heavy', '').replace('mind your step', '').replace('in what country', '').replace('you can answer with the name of the country', '').replace('your state climbs', '').replace('around the city', '').replace('voting for a city or a state', '').replace('name meanings', '').replace('system in your country', '').replace('birthday wish', '').replace('happy birthday', '').replace('app on your smart phone', '').replace('timer on your phone', '').replace('state the arguments', '').replace('what step', '').replace('testing name', '').replace('you a camera', '').replace('event name', '').replace('you have your phone', '').replace('song name', '').replace('scenes by name', '').replace('emergency response phone number', '').replace('step 1', '').replace('our zodiac signs', '').replace('step forward', '').replace('steps to help you', '').replace('opportunity to address', '').replace('state capital', '').replace('product name', '').replace('name of the marketing', '').replace('weight of the grade', '').replace('grade and its weight', '').replace('email campaign', '').replace('city service', '').replace('an email thanking', '').replace('relating to the period', '').replace('name of the movie', '').replace('name which ever form', '').replace('names such as', '').replace('names should no be', '').replace('name of shinigami', '').replace('in a city', '').replace('sending an email', '').replace('weight starts from', '').replace('life in the country', '').replace('state basketball', '').replace('move the weight', '').replace('name the length of', '').replace('simple step', '').replace('important step', '').replace('state of health', '').replace('experts state', '').replace('you can always email', '').replace('critical step', '').replace('the name jacob', '').replace('product name', '').replace('name of something', '').replace('solid state', '').replace('the name wendy', '').replace('height of an object', '').replace('enrolling in a school', '').replace('device name', '').replace('motion sensor', '').replace('just a few steps', '').replace('you can send a text', '').replace('father of our country', '').replace('income tax form', '').replace('people of the state', '').replace('governor your state', '').replace('depend on your state', '').replace('name two national', '').replace('capital of your state', '').replace('one of your state', '').replace('folder name', '').replace('name of the program', '').replace('little state', '').replace('name of the restaurant', '').replace('see more steps', '').replace('give your pet a name', '').replace("pet's name", '').replace('pets name', '').replace('pet name', '').replace('city guide', '').replace('restaurant name', '').replace('at the age of', '').replace('recipe steps', '').replace('name of the wine', '').replace('name of the sound', '').replace('gender studies', '').replace('point of this country', '').replace('ask the city', '').replace('city of toronto', '').replace('has a name', '').replace('streams of income', '').replace('name of your lunar lander', '').replace('frustrating period', '').replace('the height of the eiffel', '').replace('state leaderboard', '').replace('states battle', '').replace('make your state proud', '').replace('telephonic and email survey', '').replace('my name is alex', '').replace('email to someone', '').replace('steps are:', '').replace('everything on your calendar', '').replace('everything on their calendar', '').replace('live by that calendar', '').replace('law school', '').replace('recipe name', '').replace('application on your mobile phone','').replace('community name','').replace('name of its edible fruit','').replace('weather presenter','').replace('age of retirement','').replace('depending on date of birth','').replace('survey name','').replace('dragon name','').replace('harry potter name','').replace('mysore state','').replace('is a state in the','').replace('states reorganisation','').replace('major schools','').replace('school is best','').replace('milestone email','').replace('behavior-based email','').replace('marketing email','').replace('name of your form','').replace('name of the survey','').replace('beneath the city','').replace('names of the stations','').replace('restate','').replace('re-state','').replace('great location','').replace('city has to offer','').replace('was considered medication','').replace('names from categories','').replace('as we age','').replace('characters name','').replace("character's name",'').replace('character name','').replace('race going to be','').replace('birthday boy or girl','').replace('invalid country','')
                                
                #if a skills tells schedule, it is not asking for personal info
                if "from" in sent_lower and "to" in sent_lower:
                    sent_lower=sent_lower.replace('exercise', '').replace('exercising','')
                if "fact" in sent_lower:
                    sent_lower=sent_lower.replace('city', '')
                if "tell me a stop" in sent_lower:
                    sent_lower=sent_lower.replace('stop','location')
                if "impersonators" in sent_lower:
                    sent_lower=sent_lower.replace('phone', '').replace('zip','')
                if "pokemon" in sent_lower or "president" in sent_lower:
                    sent_lower=sent_lower.replace('name', '').replace('country', '')
                if "situp" in sent_lower or "sit-up" in sent_lower or "plank" in sent_lower or "workout" in sent_lower or "work out" in sent_lower or "pushup" in sent_lower or "exercise" in sent_lower or "walking" in sent_lower or "steps" in sent_lower or "pedometer" in sent_lower:
                    sent_lower=sent_lower.replace('situps', 'fitness activity information').replace('situp', 'fitness activity information').replace('sit-ups', 'fitness activity information').replace('sit-up', 'fitness activity information').replace('plank', 'fitness activity information').replace('workout', 'fitness activity information').replace('work out', 'fitness activity information').replace('pushup', 'fitness activity information').replace('exercise', 'fitness activity information').replace('walk', 'fitness activity information').replace('steps', 'fitness activity information').replace('step', 'fitness activity information').replace('pedometer', 'fitness activity information')
                #if a skill offers to teach a specific language, it is not really asking for personal info
                learn_language = r"learn\s+(?:the\s+)?(\w+)\s+language"
                if learn_language in sent_lower or "language diary" in sent_lower or "sign language" in sent_lower or "spoken language" in sent_lower:
                    sent_lower=sent_lower.replace('language', '')
                #if a skill asks weather for what, it is not asking about the weather but for location
                if "weather for what" in sent_lower or "based on the weather" in sent_lower:
                    sent_lower=sent_lower.replace('weather', '')
                #if a skill asks to select one of the given country names, not asking personal info
                if "say one of the following" in sent_lower:
                    sent_lower=sent_lower.replace('country', '')
                #if a skill offers to generate a password, not asking for a password
                if "password generat" in sent_lower:
                    sent_lower=sent_lower.replace('password', '')
                #if a skill just asks going to a school or college w/o specifics, not asking for location
                if "going to a school or a college" in sent_lower:
                    sent_lower=sent_lower.replace('school', '').replace('college', '')
                #miscellaneous
                sent_lower=sent_lower.replace('phone number', 'phone').replace('period of','')
                
                tokens = sent_lower.split()
                tokens_not_questions = [token for token in tokens if token not in questions and token not in remove_words]
                sent_without_questions = ' '.join(tokens_not_questions)
                
                doc=nlp(sent_without_questions) #using the trained model, extract data objs and entities
                
                for ent in doc.ents:                    
                    if ent.label_=="DATA":#extract only data objects
                        data_obj = ent.text
                        data_obj = data_obj.translate(str.maketrans('', '', string.punctuation)) #remove punctuation
                        all_practices.append((data_obj)) #store all extracted practices in a list, 'all_practices'
                        
                        #match the extracted ents with the practices list, if data_obj is matched as a substring, store in list
                        for practice in practices:
                            if data_obj == practice.lower():# instead of using in, use == to avoid subword match
                                sensitive_practices.append(data_obj)
                                
                matches = practices_pattern.findall(sent_without_questions)
                for match in matches:
                    if match.lower() not in sensitive_practices:
                        sensitive_practices.append(match.lower())
                    
                isinformation=False #reset the variable
            isinformation=False #reset the variable          
        i=1
    
    #ensuring unique values in sensitive_practices
    sensitive_practices = set(sensitive_practices)
    sensitive_practices = list(sensitive_practices)
    print("sensitive_practices: ",sensitive_practices)
    
    return sensitive_practices, all_practices, text
            


# In[ ]:


#practice declarations from policies

def readPolicy():
    #read skill id and name    
    with open("skillinfo.txt", "r", encoding="ISO-8859-1") as file:
        skill_name = file.readline().rstrip()
        ASIN = file.readline().rstrip()
        skill_id = file.readline().rstrip()
    
    #retrieve the privacy policy declarations of practices
    query = f"SELECT * FROM PrivacyPolicyExtractRealTime where skill_id = '{skill_id}'"
    cursor.execute(query)
    policy_practices = cursor.fetchall()
        
    return skill_name,skill_id,ASIN,policy_practices


# In[ ]:


def complianceCheck(sensitive_practices, policy_practices,skill_name,ASIN,skill_id,text):
    
    disclosure_type=''
    data_synonyms = {}
    compliance_results=[] #a list of lists
    individual_results=[] #a flat list
    
    policy_practice_clean=''
    
    #a dict of ontologies/synonyms for each skill practice returned by readOutput().
    for data_obj in sensitive_practices:
        if data_obj.lower() == 'address' or data_obj.lower() == 'name' or data_obj.lower() == 'age':
            query = f"SELECT * FROM PrivacyTermSynonym WHERE term = '{data_obj}'"#in case of address, don't want email address and ip address
        else:
            query = f"SELECT * FROM PrivacyTermSynonym WHERE term LIKE '%{data_obj}%'"
        cursor.execute(query)
        terms_synonyms = cursor.fetchall()
        
        #converting tuple list to dict
        for term,syn in terms_synonyms:
            data_synonyms.setdefault(term, []).append(syn)
        
        if (data_obj.lower() == 'address') or (data_obj.lower() == 'city'):
            query1 = f"SELECT generic_term FROM ontology WHERE data = '{data_obj}'"
        else:
            query1 = f"SELECT generic_term FROM ontology WHERE data LIKE '%{data_obj}%'"
        cursor.execute(query1)
        generic_type = cursor.fetchall()
        if len(generic_type)>0:
            gen_term= '{}'.format(generic_type[0][0]) #convert the tuple list item (personal/non-personal) to str 'gen_term'
        else:
            gen_term="nonpersonal" #some non-personal data terms are not populated in ontology table, so if match not found, with data_obj, the generic_term will be nonpersonal
        
        gen_term=gen_term.translate(str.maketrans('', '', string.punctuation)).lower().strip() #remove punc from gen_term
        
        #all values in the data_synonyms dict returned as a list of lists.   
        value_results = [val for key, val in data_synonyms.items()]
        value_results_flat = [item for sublist in value_results for item in sublist] #flatten a list of lists to a list
        
        data_synonyms.clear()
        
        #also find and add the data_obj lemma to the list in the next step if it is the first occurance of noun. Second noun is usually meaningless eg in phone number, want phone only
        doc1=nlp(data_obj)
        noun_found=False #variable to control saving only the first noun
        first_noun=''
        for tok in doc1:
            if tok.pos_ == 'NOUN' and noun_found==False:
                first_noun = tok.lemma_
                noun_found=True
        
        if len(value_results_flat) > 0:
            data = value_results_flat
            data.append(data_obj) #also add the original data_obj (skill practice term) to the list
            if first_noun != '':
                data.append(first_noun)
        else:
            data = list(data_obj.split("_@_")) #convert to list while preventing the splitting (by default, would split into separate characters).
            if first_noun != '':
                data.append(first_noun)
    
        data = [item.translate(str.maketrans('', '', string.punctuation)).lower().strip() for item in data] #remove punc, spaces, and to lower case
        
        #If there was no privacy policy for the skill or no privacy declarations in the policy, policy_practices would be empty
        if len(policy_practices) ==0:
            disclosure_type = 'Undisclosed'
            individual_results=[ASIN,skill_id,skill_name,disclosure_type,data_obj,text,'','','']
        
        unclear_disclosure = False
        inaccurate_disclosure = False
        
        for policy_practice in policy_practices:
            
            #clean up the policy practice: remove punc, to lower, split and join after removing remove_words
            tokens = policy_practice[3].translate(str.maketrans('', '', string.punctuation)).lower().split()
            tokens_final = [token for token in tokens if token not in remove_words]
            policy_practice_clean = ' '.join(tokens_final)
            
            #handle case about ip address, email address, home address matching incorrectly and other similar cases...
            policy_practice_clean=policy_practice_clean.replace('email address', 'email').replace('usage','')
            policy_practice_clean=policy_practice_clean.replace('ip address', 'ip').replace('i p address', 'ip')
            
            #find noun lemmas in policy_practice_clean as well for better chance of match with the data list. Data list already has data_obj lemma
            policy_practice_nouns=[]
            doc2=nlp(policy_practice_clean)
            for tok in doc2:
                if tok.pos_ == 'NOUN':
                    policy_practice_nouns.append(tok.lemma_)
            
            if (any (word in (policy_practice_clean) for word in data) or any (word in (policy_practice_nouns) for word in data)) and (policy_practice[2] =='not_collect'):
                disclosure_type = 'Inaccurate'
                individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,policy_practice[2],policy_practice_clean,policy_practice[5]]
                break #once any match is found, break so not overwritten by unclear/undisclosed privacy practice cases
            #if word in the list 'data' are present in the policy practice sent *OR* present in the privacy practice noun lemmas *AND* the verb is suitable
            elif (any (word in (policy_practice_clean) for word in data) or any (word in (policy_practice_nouns) for word in data)) and (policy_practice[2] =='collect'):
                disclosure_type = 'Disclosed'
                individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,policy_practice[2],policy_practice_clean,policy_practice[5]]
                break #once any match is found, break so not overwritten by unclear/undisclosed privacy practice cases
            #else if the case for Unclear considering ontologies
            elif (not any (word in (policy_practice_clean) for word in data) and not any (word in (policy_practice_nouns) for word in data)):                
                if ('information' in policy_practice_clean) or ('data' in policy_practice_clean):
                    if ('nonpersonal' in policy_practice_clean) or ('nonpersonally' in policy_practice_clean):
                        if(gen_term == "personal") and (unclear_disclosure == False) and (inaccurate_disclosure==False) and (policy_practice[2] =='collect'):#data_obj is personal
                            disclosure_type = 'Undisclosed'
                            individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,'','','']
                        elif(gen_term == "personal") and (policy_practice[2] =='not_collect'):
                            disclosure_type = 'Inaccurate'
                            individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,policy_practice[2],policy_practice_clean,policy_practice[5]]
                            inaccurate_disclosure=True
                        elif(gen_term == "nonpersonal") and (inaccurate_disclosure==False) and (policy_practice[2] =='collect'):
                            disclosure_type = 'Unclear'
                            unclear_disclosure = True
                            individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,policy_practice[2],policy_practice_clean,policy_practice[5]]
                        elif(gen_term == "nonpersonal") and (policy_practice[2] =='not_collect'):
                            disclosure_type = 'Inaccurate'
                            inaccurate_disclosure=True
                            individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,policy_practice[2],policy_practice_clean,policy_practice[5]]
                            
                    elif ('personal' in policy_practice_clean) or ('personally' in policy_practice_clean):
                        if (gen_term == "nonpersonal") and (unclear_disclosure == False) and (inaccurate_disclosure==False) and (policy_practice[2] =='collect'):#data_obj is non-personal
                            disclosure_type = 'Undisclosed'
                            individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,'','','']
                        elif (gen_term == "nonpersonal") and (unclear_disclosure == False) and (inaccurate_disclosure==False) and (policy_practice[2] =='not_collect'):#data_obj is non-personal
                            disclosure_type = 'Undisclosed'
                            individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,policy_practice[2],policy_practice_clean,policy_practice[5]]                            
                        elif(gen_term == "personal") and (inaccurate_disclosure==False) and (policy_practice[2] =='collect'):
                            disclosure_type = 'Unclear'
                            unclear_disclosure = True
                            individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,policy_practice[2],policy_practice_clean,policy_practice[5]]
                        elif(gen_term == "personal") and (policy_practice[2] =='not_collect'):
                            disclosure_type = 'Inaccurate'
                            inaccurate_disclosure==True
                            individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,policy_practice[2],policy_practice_clean,policy_practice[5]]                            
                    else:
                        if(gen_term == "personal") and (unclear_disclosure == False) and (inaccurate_disclosure==False) and (policy_practice[2] =='collect'):#data_obj is personal
                            disclosure_type = 'Undisclosed'
                            individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,'','','']
                        elif(gen_term == "personal") and (policy_practice[2] =='not_collect'):#data_obj is personal
                            disclosure_type = 'Inaccurate'
                            individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,policy_practice[2],policy_practice_clean,policy_practice[5]]
                            inaccurate_disclosure=True                        
                        elif(gen_term == "nonpersonal") and (inaccurate_disclosure==False) and (policy_practice[2] =='collect'):
                            disclosure_type = 'Unclear'
                            unclear_disclosure = True
                            individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,policy_practice[2],policy_practice_clean,policy_practice[5]]
                        elif(gen_term == "nonpersonal") and (policy_practice[2] =='not_collect'):
                            disclosure_type = 'Inaccurate'
                            inaccurate_disclosure=True
                            individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,policy_practice[2],policy_practice_clean,policy_practice[5]]                    
            else:
                if unclear_disclosure == False and inaccurate_disclosure==False:
                    disclosure_type = 'Undisclosed'
                    individual_results=[ASIN,policy_practice[0],skill_name,disclosure_type,data_obj,text,'','','']
                    print("individual_results1: ",individual_results)
                    
        #may have never entered the above loop, because eg if policy_practice_clean=0 for all the practices: undisclosed in this case
        if len(individual_results) ==0:
            disclosure_type = 'Undisclosed'
            individual_results=[ASIN,skill_id,skill_name,disclosure_type,data_obj,text,'','','']

        if disclosure_type == 'Undisclosed' or disclosure_type == 'Inaccurate':
            print("individual_results2: ",individual_results)
            
            #check user whitelist to allow collection from these skills.
            query2 = f"SELECT skill_name FROM whitelist_skills WHERE skill_name = '{skill_name}'"
            cursor.execute(query2)
            skill_name_query2 = cursor.fetchall()
            if len(skill_name_query2)>0:
                print("\n Inconsistency detected, not STOPPING the skill as it is whitelisted by the user. \n")
            else:
                print("\n Alert, alert, the skill attempts to collect your", data_obj, "without disclosure.\n")
                
                with open(warn_msg, 'w') as wm:
                    wm.write("Alert, alert, the skill attempts to collect your "+ data_obj + " without disclosure.")
                    wm.close()
                
                with open(stop_msg, 'w') as f:
                    f.write("STOP")
                    f.close()
        
        print("individual_results3: ",individual_results)
        compliance_results.append(individual_results)
        print("compliance_results: ",compliance_results)
        individual_results=[] #reset the individual_results list
    
    return compliance_results
    


# In[ ]:


#save compliance_results in a csv
def save_results(compliance_results):
    with open('compliance_results.csv', mode='a', newline='') as result:
        result_writer = csv.writer(result)
        for record in compliance_results:
            result_writer.writerow(record)


# In[ ]:


if __name__ == "__main__":
    while True:
        main()


# In[ ]:


#JA-
#Eunomia-1-main code for compliance validation.


# In[ ]:




