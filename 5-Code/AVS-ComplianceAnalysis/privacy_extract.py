#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#JA-
#Eunomia-3-extract privacy policy declarations (keyword-based).


# In[ ]:


import pyodbc
import time
import shutil
import os
import re
import csv


# In[ ]:


conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=AVALON\SQLEXPRESS;'
                      'Database=AVSPrivacyCompliance;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()


# In[ ]:


# verbs of interest as these indicate collection, use, sharing, etc. of user data.
verbs_of_interest = ['collect', 'sell', 'use', 'disclose',
         'transfer', 'share','do not collect','does not collect',"doesn't collect", 'do not use','does not use', "don't use"]

# negated verbs, showing some practices not taking place.
verbs_negated=['do not collect','does not collect',"doesn't collect", 'do not use','does not use', "don't use","doesn't use"]

# identify the following practices in the policy sentences
#These practices were generated automatically using the BERT model. Also, added to it few practices that SkillDetective provided
practices = [ 'Email','email','e-mail', 'Birthday', 'Age', 'Gender', 'Location',
'Contact', 'Phonebook', 'phone','telephone', 'Profession', 'Income', 'Zipcode', 'Postal code','postcode',
'Phone number', 'Passport number', 'Driver license number','Driver license', 'Bank account number', 'Debit card number', 'Credit card number', 'SSN',
'Height', 'Weight', 'Blood group', 'Blood pressure', 'Blood glucose', 'Blood Oxygen', 'Heart rate', 'Body temperature', 'Sleep data', 'Fat percentage',
'Mass index', 'Waist circumference', 'Menstruation', 'Period','pregnancy','medication','pill',
'Phone number','SSN', 'Email address',
'Internet protocol address', 'Age', 'Gender', 'Birthday', 'Medical record number', 'Health plan beneficiary number', 'Driver license number', 'ethnicity', 
'affiliation', 'orientation', 'zip code', 'first name', 'last name', 'full name',
'social security number', 'bank account number','email address','account user info','phone','account details',
'photo','health and wellness','social media information','geographical location','payment',
'organization info','motion','weather','calendar','camera','sim serial number','text message','phone number',
'browser information','operating system','ip address','ip','payment card information',
'date of birth','application information','network information','internet service provider','advertising id',
'android id','imei','device identifier','payment method','ssn','payment card expiration date','purchase date','purchase amount',
'travel information','vehicle information','salary','vehicle identification number','fitness activity information',
'employment information','body weight','operating system','browser information','browser history','browser type',
'device setting','device type','business information','email address','website address','mac address',
'government-issue identification information','education level','application information','date of birth','birth year',
'bank routing number','educational information','ip address','contact information','security code','physical traits',
'social media account credential','social media friends','social media profile url','social media username',
'social media account information','social media information','credential','browsing behavior','browser information','employer name','business name','photo','race','gender','school','phone tower','biography',
'profile information','isp','internet service provider','insurance coverage information','medical insurance information',
'insurance history','insurance carrier','insurance policy number','state','city','zip code','country','registration information',
'membership information','password','internet browse history','lifestyle information','facebook profile information',
'credit history','blood glucose level','heart rate','call log','education information','interaction information',
'philosophical belief','relationship status','political view','activity information','purchase information',
'shopping habits','biometric information','genetic information','payment card information','payment card number',
'payment information','text message','text and multimedia messaging','disability','allergy','credit score','shipping information','account balance information',
'phone number','operating system','photo metadata','operating system version','body mass index','credit card security code',
'identifier','blood pressure','emergency contact information','contact information','postal address',
'transaction information','financial transaction information','accelerometer information','device information',
'prescription information','geocaching log','account information','credit information','license number',
'financial account information','bank account number','driver license information','driver license number',
'vehicle license number','username','serial number','address book','addresses','Address','address','health and wellness','person age','network information',
'traffic information','log information','demographic information','person name','contact name','sexual orientation',
'sexual history','user information','gps','geographical location','weather','phone','calendar','payment','camera',
'account user info','account details','sim serial number','gallery','zodiac','sit-up','situp','plank','workout','work out',
'pushup','exercise','timezone','step','steps','pedometer','street name','Name','street number','geolocation', 
'non-personal information', 'personal information','non-personally identifying information','non-personally identifiable information',
'personally identifiable information','information','non-personal data','personal data','data',
'bithday','demographic info','Photos','Purchase history','usage information','vehicle usage information',
#common data types related to privacy labels per iOS
'crash data','crash information', 'performance data','performance information','diagnostic data','contacts','video','audio','customer support','browsing','search history','purchase','interaction data','usage data','advertising data','advertising information']

# create patterns from practices, verbs of interest and negated verbs.
pattern_for_practices = r'(?<!\w)(?:' + '|'.join(practices) + r')(?!\w)'
pattern_for_verbs = r'(?<!\w)(?:' + '|'.join(verbs_of_interest)  + r')(?!\w)'
pattern_for_ipaddr = r'\bip address\b'
pattern_for_negverb = r'(?<!\w)(?:' + '|'.join(verbs_negated)  + r')(?!\w)'

# path to the policy files to be analyzed for privacy declarations
path_policy_files = '../../privacypolicies/files'

#maintain a record of policy files in a txt file
record_of_files = "../../privacypolicies/records/record.txt"
record_file_stamp=0; #track of the updation of records file

while (True):
    #wait until the records file is absent or has size 0 or hasn't changed recently
    while not os.path.exists(record_of_files):
        time.sleep(1)
    while os.stat(record_of_files).st_size == 0:
        time.sleep(1)
    try:
        while ((os.path.getmtime(record_of_files))==record_file_stamp):
            time.sleep(1)
    except FileNotFoundError:
        print ("File is not present")
        while not os.path.exists(record_of_files):
            time.sleep(1)
    
    print("Existing time stamp: ", record_file_stamp)
    record_file_stamp=os.path.getmtime(record_of_files);
    print("Updated time stamp: ", record_file_stamp)    
    
    # loop over the contents (policy files) of the directory to process one file at a time
    for policyfile in os.listdir(path_policy_files):
        #create privacy policy file path
        policy_file_path = os.path.join(path_policy_files, policyfile)
        file_done_path = os.path.join(path_policy_files,'done', policyfile) #done folder for files when finished processing

        # ignore the directories, process files only
        if not os.path.isfile(policy_file_path):
            continue

        # open the file, get contents for analysis
        with open(policy_file_path, 'r',encoding='utf-8', errors='ignore') as file:
            file_contents = file.read()
            print ("The path of the file is: ", policy_file_path)
    
    
        #some phrases need to be replaced as per their intended meaning.
        file_contents = re.sub(r'network activity information', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'We take steps to', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'will take steps to', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'will take all the steps', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'take a number of steps', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'physical and email addresses','address and email', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'email addresses','email', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'email address', 'email', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Internet Protocol (IP) address', 'ip address', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'for more information', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'to exercise them', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'please contact', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'for more information', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'trading name', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'time period', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'data shown in the comments', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'What personal data we collect and why', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'addresses the use', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'maintained on - computers located outside of your state, province, country or other governmental jurisdiction where the data protection laws may differ from those of your jurisdiction', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'address technical issues', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'under the age of 18', '', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'third parties located outside of your country','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'The City of Hamilton','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'outside of your home country','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'file name','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'email newsletter','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'wifi name','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'name of the wifi','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'user name','username', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'appropriate steps','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'exercise our legal rights','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'exercise the choices','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'exercise, or defend','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'exercise your rights','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'domain name','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'may not use the name','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'any other names or Trademarks','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'MINIMUM AGE REQUIREMENT','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'at least 18 years old','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'legal age','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'age is greater','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'under the age of','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'rights as a data subject','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'use of Birthday Wisher','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'name of the domain','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r"mobile carrier's name",'', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'City service','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'City of Boston','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'CITY HALL','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'intent of the City','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'the City may use','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'interacting with the City','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'defense of the City','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'The City reserves','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'the City seal','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'the City will use','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'The City also','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'The city is','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'acceptable to City','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'the City permission','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'The City contracts','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'articles and information','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'information and updates','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Exercise Roulette App','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'alter information','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'device Internet Protocol \(\“IP\”\) address','ip address', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'device Internet Protocol (â€œIPâ€) address','ip address', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'device Internet Protocol \(\"IP\"\) address','ip address', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Samsung Phone','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'device name','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'message information','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Orc Name Generator','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'ARCHIVE Birthday Greetings','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'address anyone','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'user name and password','username', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Internet Protocol \(IP\) address','ip address', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'LocationsearchAndroid Apps','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'device state','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'please email us','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'alterations to the Data','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Your use of the Data','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Your receipt and use of the Data','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'with respect to the Data','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'use the Data','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'order to use the Data','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'in connection with the Data','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'loss of the Data','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'inability to use the Data','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'and redistribute the Data','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'data made available','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'resulting loss of data','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Your use of the information','', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'non-personally-identifiable information','non-personally identifiable information', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'city-level','city', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Skill requests sometimes include','we collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'This allows us to save','we collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'we ask for','we collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Collected Information','we collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'may include information such as','we collect information', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'collects such information','we collect information', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'we ask','we collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'is stored in the database','we collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Personal Information that directly identify you','we collect personal information', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Skill utilizes','we collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'uses your','we collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Personally identifiable information may include','we collect personal information', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'We store','we collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'information is collected','we collect information', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'data collected','we collect data', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'can be provided','we collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'We never collect','we do not collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'We don’t store','we do not collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'We don''t store','we do not collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'We may ask You','we collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'not using any of user data','we do not collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'require you to enable sharing','we collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'neither request nor collect','we do not collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'may request at any time access to such data','we collect data', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'This information is collected','we collect information', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'may collect certain information','we collect information', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'can only be retrieved','we collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'This information is used','we collect information', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'you may be asked to','we collect information', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'We do not sell','we collect information', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Reasons for text messages include the following','we collect information-sentid1', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'Personal Data may include information considered sensitive in some jurisdictions','we collect personal information-sentid2', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'The Personal Information that I collect is used for providing and improving the Service or to send information','we collect personal information-sentid3', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r'This policy covers how Keon Jukes treats personal information that is collected or received through the services we provide. Personal information is information about you that is personally identifiable like your','we collect personal information-sentid4', file_contents, flags=re.IGNORECASE)    
        file_contents = re.sub(r'our service providers will use the information that you provide to respond to','we collect information-sentid5', file_contents, flags=re.IGNORECASE)    
        file_contents = re.sub(r'The Company collects and processes the following data about you','we collect information-sentid6', file_contents, flags=re.IGNORECASE)    
        file_contents = re.sub(r'Examples of such instances may be providing us your','we collect information-sentid7', file_contents, flags=re.IGNORECASE)    
        file_contents = re.sub(r'Information that You give us – Personal data including','we collect personal data-sentid8', file_contents, flags=re.IGNORECASE)    
        file_contents = re.sub(r'Examples of Personal Information collected:','we collect personal information-sentid9', file_contents, flags=re.IGNORECASE)    
        file_contents = re.sub(r'These logs may contain some personally identifying information','we collect personal information-sentid10', file_contents, flags=re.IGNORECASE)    
        file_contents = re.sub(r'is used','we collect', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r',',' ', file_contents, flags=re.IGNORECASE)
        file_contents = re.sub(r"'",'', file_contents, flags=re.IGNORECASE)

        unique_practice_tuples = set() # to hold practice tuples
        
        # create sentences from the policy content
        individual_sents = re.split(r'[.?]+', file_contents)
        prev_sent = individual_sents[0].strip()
        
        for i in range(1, len(individual_sents)):
            curr_sent = individual_sents[i].strip()

            # matching patterns for practices, verbs, etc. in the current sentence.
            practice_pattern_match = re.findall(pattern_for_practices, curr_sent, re.IGNORECASE)
            verb_pattern_match = re.search(pattern_for_verbs, curr_sent, re.IGNORECASE)
            negverb_pattern_match = re.search(pattern_for_negverb, curr_sent, re.IGNORECASE)
            ipaddress_pattern_match = re.search(pattern_for_ipaddr, curr_sent, re.IGNORECASE)
        
            if practice_pattern_match and verb_pattern_match:
                verb_match = verb_pattern_match.group(0) # matched verb
                # what is the generic verb term: collect or not_collect?
                if negverb_pattern_match:
                    verb_collect_notcollect='not_collect'
                else:
                    verb_collect_notcollect='collect' 
                    #identify privacy practice tuples and then add them to the set of the identified tuples
                for practice_matched in practice_pattern_match:
                    tuple_created = (f"{policyfile.replace('.txt', '')},|,we,|,{verb_collect_notcollect},|,{practice_matched.lower()},|,{verb_match.lower()},|,{curr_sent}")
                    unique_practice_tuples.add(tuple_created)
                    pre_verb = verb_match
            elif ipaddress_pattern_match and practice_pattern_match:
                for practice_matched in practice_pattern_match:
                    tuple_created=(f"{policyfile.replace('.txt', '')},|,we,|,{verb_collect_notcollect},|,{practice_matched.lower()},|,{pre_verb.lower()},|,{curr_sent}")
                    unique_practice_tuples.add(tuple_created)
            else:
                # the current sentence doesn't have the verb, so expand the search over previous and current sentence for declared practice over multiple sentences.
                merged_sent = prev_sent + ' ' + curr_sent

                # pattern match in the merged sentence
                merged_sent_practice = re.findall(pattern_for_practices, merged_sent, re.IGNORECASE)
                prev_verb_match = re.search(pattern_for_verbs, prev_sent, re.IGNORECASE)
                merged_sent_negverb = re.search(pattern_for_negverb, merged_sent, re.IGNORECASE)
                merged_sent_ipaddress = re.search(pattern_for_ipaddr, merged_sent, re.IGNORECASE)
            
                if merged_sent_practice and prev_verb_match:
                    verb_match = prev_verb_match.group(0)
                    #identify collect/not collect verbs
                    if merged_sent_negverb:
                        verb_collect_notcollect='not_collect'
                    else:
                        verb_collect_notcollect='collect'
                    # identify tuples in the merged sentences and then add tuples to the set.
                    for practice_matched in merged_sent_practice:
                        tuple_created=(f"{policyfile.replace('.txt', '')},|, we,|,{verb_collect_notcollect},|,{practice_matched.lower()},|,{verb_match.lower()},|,{merged_sent}")
                        unique_practice_tuples.add(tuple_created)
                        pre_verb = verb_match
                elif merged_sent_ipaddress and merged_sent_practice:
                    for practice_matched in merged_sent_practice:
                        tuple_created=(f"{policyfile.replace('.txt', '')},|, we,|,{verb_collect_notcollect},|,{practice_matched.lower()},|,{pre_verb.lower()},|,{merged_sent}")
                        unique_practice_tuples.add(tuple_created)

            prev_sent = curr_sent
        
        for tuple_created in unique_practice_tuples:
            # save the tuples in the DB
            tokens = tuple_created.split(",|,")
            cursor.execute("INSERT INTO PrivacyPolicyExtractRealTime (skill_id, entity, verb, object, original_verb, sentence) VALUES (?,?,?,?,?,?)",(tokens[0].strip(),tokens[1].strip(),tokens[2].strip(),tokens[3].strip(),tokens[4].strip(),tokens[5].strip()))
            cursor.commit()
            print(tuple_created)
        
        # upon completing the file analysis, move the file to the done path
        shutil.move(policy_file_path, file_done_path)
        print("Done folder file transfer. \n\n")


# In[ ]:


#JA-
#Eunomia-3-extract privacy policy declarations (keyword-based).


# In[ ]:




