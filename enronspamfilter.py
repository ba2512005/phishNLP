# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 15:00:44 2017
@author: Abhijeet Singh
"""

import os
import numpy as np
import time
from collections import Counter
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords

from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import confusion_matrix
from sklearn.svm import LinearSVC
from sklearn.metrics import jaccard_similarity_score
from sklearn.calibration import CalibratedClassifierCV
import pandas as pd

start_time = time.time()

def extract_tokens(dfa):
    review_tokenized = []
    lmt = WordNetLemmatizer()
    for df in dfa:
        tokenize_words = word_tokenize(df.lower(),language='english')
        pos_word = pos_tag(tokenize_words)
        tokenize_words = ["_".join([lmt.lemmatize(i[0]),i[1]]) for i in pos_word if (i[0] not in stopwords.words("english") and len(i[0]) > 2)]
        review_tokenized.append(tokenize_words)
    dfo = review_tokenized
    return dfo


def make_Dictionary(root_dir):
    emails_dirs = [os.path.join(root_dir,f) for f in os.listdir(root_dir)]    
    all_words = []       
    for emails_dir in emails_dirs:
        dirs = [os.path.join(emails_dir,f) for f in os.listdir(emails_dir)]
        for d in dirs:
            emails = [os.path.join(d,f) for f in os.listdir(d)]
            for mail in emails:
                with open(mail) as m:
                    for line in m:
                        words = line.split()
                        #words1 = extract_tokens(words)
                        all_words += words#1
    dictionary = Counter(all_words)
    list_to_remove = dictionary.keys()
    
    for item in list_to_remove:
        if item.isalpha() == False: 
            del dictionary[item]
        elif len(item) == 1:
            del dictionary[item]
    dictionary = dictionary.most_common(3000)
    
    return dictionary
    
def extract_features(root_dir): 
    emails_dirs = [os.path.join(root_dir,f) for f in os.listdir(root_dir)]  
    docID = 0
    features_matrix = np.zeros((33716,3000))
    train_labels = np.zeros(33716)
    for emails_dir in emails_dirs:
        dirs = [os.path.join(emails_dir,f) for f in os.listdir(emails_dir)]
        for d in dirs:
            emails = [os.path.join(d,f) for f in os.listdir(d)]
            for mail in emails:
                with open(mail) as m:
                    all_words = []
                    for line in m:
                        words = line.split()
                        all_words += words
                    for word in all_words:
                      wordID = 0
                      for i,d in enumerate(dictionary):
                        if d[0] == word:
                          wordID = i
                          features_matrix[docID,wordID] = all_words.count(word)
                train_labels[docID] = int(mail.split(".")[-2] == 'spam')
                docID = docID + 1                
    return features_matrix,train_labels
    
#Create a dictionary of words with its frequency


#dictionary = make_Dictionary(root_dir)


#Prepare feature vectors per training mail and its labels

#features_matrix,labels = extract_features(root_dir)
#np.save('enron_features_matrix.npy',features_matrix)
#np.save('enron_labels.npy',labels)


def trainer_loader(root_dir):
    if not (os.path.isfile(root_dir+'_features_matrix.npy') and os.path.isfile(root_dir+'_labels.npy')):
        input( "features not found")
        features_matrix,labels = extract_features(root_dir)
        np.save(root_dir+'_features_matrix.npy', features_matrix)
        np.save(root_dir+'_labels.npy', labels)
    else:
        features_matrix = np.load(root_dir+'_features_matrix.npy')
        labels = np.load(root_dir+'_labels.npy')
        
    if not os.path.isfile('dict_'+root_dir+'.npy'):
         input( "dict not found")
         dictionary = make_Dictionary(root_dir)
         np.save('dict_'+root_dir+'.npy',dictionary)
    else:
         dictionary = np.load('dict_'+root_dir+'.npy')

    return features_matrix,labels,dictionary

def predicter(email):
    start_time1 = time.time()
    root_dir = 'enron'
    features_matrix,labels,dictionary = trainer_loader(root_dir)
    X_train, X_test, y_train, y_test = train_test_split(features_matrix, labels, test_size=.6)

    #model1 = LinearSVC(tol = .000000000001)
    model2 = MultinomialNB()
    model2.fit(X_train,y_train)
    
    
    #clf = CalibratedClassifierCV(model1)
    #model1.fit(X_train,y_train)

    line_matrix = np.zeros((1,3000))
    all_words = email.split()
    for word in all_words:
      wordID = 0
      for i,d in enumerate(dictionary):
        if d[0] == word:
          wordID = i
          line_matrix[0,wordID] = all_words.count(word)


    result1 = model2.predict(line_matrix)
    return result1
    #y_proba = model1.predict_proba(line_matrix)
    print "classification:" + str(result1)
    #print "Probability: " + str(y_proba)
    
def tester():
    root_dir = 'enron'
    features_matrix,labels,dictionary = trainer_loader(root_dir) 
    

    ##print features_matrix.shape
    ##print labels.shape
    ##print sum(labels==0),sum(labels==1)
    
    records = []
    datetimes = []
    for i in range (0,2):
        start_time1 = time.time()
        X_train, X_test, y_train, y_test = train_test_split(features_matrix, labels, test_size=.6)

        ## Training models and its variants

        model1 = LinearSVC(tol = .001)
        
        #clf = CalibratedClassifierCV(model1)
        #clf.fit(X_train,y_train)
        model1.fit(X_train,y_train)

        result1 = model1.predict(X_test)
        #y_proba = clf.predict_proba(X_test)
        #print "Probability: " + str(y_proba)
        ##print confusion_matrix(y_test, result1)
        ##print 'Accuracy: ' + str(jaccard_similarity_score(y_test, result1)*100)[0:5] + "%"

        elapsed_time = time.time() - start_time1
        datetimes.append(elapsed_time)
        records.append(jaccard_similarity_score(y_test, result1))
        
        #print "Time elapsed: " + str(elapsed_time)[0:4] + 'seconds'
       
        
    print reduce(lambda x, y: x + y, records) / len(records)
    print reduce(lambda x, y: x + y, datetimes) / len(datetimes)
    
    print time.time()-start_time

msg = '''To start off, I have a 6 new videos + transcripts in the members section. In it, we analyse the Enron email dataset, half a million files, spread over 2.5GB. It's about 1.5 hours of  video.
I have also created a Conda environment for running the code (both free and member lessons). This is to ensure everyone is running the same version of libraries, preventing the Works on my machine problems. If you get a second, do you mind trying it here?'''   
msg2 = '''As one of our top customers we are providing 10% OFF the total of your next used book purchase from www.letthestoriesliveon.com. Please use the promotional code, TOPTENOFF at checkout. Limited to 1 use per customer. All books have free shipping within the contiguous 48 United States and there is no minimum purchase.
We have millions of used books in stock that are up to 90% off MRSP and add tens of thousands of new items every day. Don’t forget to check back frequently for new arrivals.'''

for i in range(0,5):
    print predicter(msg)

