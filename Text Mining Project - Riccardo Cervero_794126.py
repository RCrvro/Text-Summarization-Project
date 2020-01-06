###TEXT MINING PROJECT
###RICCARDO CERVERO, 794126

#Import packages
import numpy as np
import pandas as pd
import re
import nltk
nltk.download('punkt')
nltk.download('stopwords')
stop_words = stopwords.words('english')
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
import matplotlib.pyplot as plt

## 0. TEXT PREPROCESSING

#List of contractions to transform
contractions = {"ain't": "is not", "aren't": "are not","can't": "cannot", "'cause": "because", "could've": "could have", "couldn't": "could not",
                           "didn't": "did not",  "doesn't": "does not", "don't": "do not", "hadn't": "had not", "hasn't": "has not", "haven't": "have not",
                           "he'd": "he would","he'll": "he will", "he's": "he is", "how'd": "how did", "how'd'y": "how do you", "how'll": "how will", "how's": "how is",
                           "I'd": "I would", "I'd've": "I would have", "I'll": "I will", "I'll've": "I will have","I'm": "I am", "I've": "I have", "i'd": "i would",
                           "i'd've": "i would have", "i'll": "i will",  "i'll've": "i will have","i'm": "i am", "i've": "i have", "isn't": "is not", "it'd": "it would",
                           "it'd've": "it would have", "it'll": "it will", "it'll've": "it will have","it's": "it is", "let's": "let us", "ma'am": "madam",
                           "mayn't": "may not", "might've": "might have","mightn't": "might not","mightn't've": "might not have", "must've": "must have",
                           "mustn't": "must not", "mustn't've": "must not have", "needn't": "need not", "needn't've": "need not have","o'clock": "of the clock",
                           "oughtn't": "ought not", "oughtn't've": "ought not have", "shan't": "shall not", "sha'n't": "shall not", "shan't've": "shall not have",
                           "she'd": "she would", "she'd've": "she would have", "she'll": "she will", "she'll've": "she will have", "she's": "she is",
                           "should've": "should have", "shouldn't": "should not", "shouldn't've": "should not have", "so've": "so have","so's": "so as",
                           "this's": "this is","that'd": "that would", "that'd've": "that would have", "that's": "that is", "there'd": "there would",
                           "there'd've": "there would have", "there's": "there is", "here's": "here is","they'd": "they would", "they'd've": "they would have",
                           "they'll": "they will", "they'll've": "they will have", "they're": "they are", "they've": "they have", "to've": "to have",
                           "wasn't": "was not", "we'd": "we would", "we'd've": "we would have", "we'll": "we will", "we'll've": "we will have", "we're": "we are",
                           "we've": "we have", "weren't": "were not", "what'll": "what will", "what'll've": "what will have", "what're": "what are",
                           "what's": "what is", "what've": "what have", "when's": "when is", "when've": "when have", "where'd": "where did", "where's": "where is",
                           "where've": "where have", "who'll": "who will", "who'll've": "who will have", "who's": "who is", "who've": "who have",
                           "why's": "why is", "why've": "why have", "will've": "will have", "won't": "will not", "won't've": "will not have",
                           "would've": "would have", "wouldn't": "would not", "wouldn't've": "would not have", "y'all": "you all",
                           "y'all'd": "you all would","y'all'd've": "you all would have","y'all're": "you all are","y'all've": "you all have",
                           "you'd": "you would", "you'd've": "you would have", "you'll": "you will", "you'll've": "you will have",
                           "you're": "you are", "you've": "you have"}

#Function to transform the contraction in the extended form
def rem_contractions(x):
  x = str(x).split()
  new_text = []
  for word in x:
    if word in contractions:
      new_text.append(contractions[word])
    else:
      new_text.append(word)
  return ' '.join([str(elem) for elem in new_text])

#Function to apply preprocessing operations
def text_preprocessing(x,remove_stopwords=True):
  cleaned = rem_contractions(x)
  cleaned = pd.Series(cleaned).str.replace("[^a-zA-Z]", " ") #punctuation, special characters and numbers
  cleaned = [s.lower() for s in cleaned] #to lowercase
  if remove_stopwords: 
    cleaned = " ".join([i for i in cleaned if i not in stop_words]) 
  #No stemming because it could cause a loss of information
  return cleaned

## 1. TOPIC FOCUSED

# 1.1 LATENT SEMANTIC ANALYSIS

def weighting(input,weight):
  #Preprocess the input
  sentences_cleaned = [text_preprocessing(y) for y in (sent_tokenize(input))]
  #Compute occurence of each word for each sentence
  DFs = []
  if weight == "f":
    for sent in sentences_cleaned:
      tokens = nltk.word_tokenize(sent)
      tokens2 = pd.DataFrame(tokens)
      tokens2.columns=['Frequency']
      tokens2 = pd.DataFrame(tokens2.Frequency.value_counts())
      tokens2 = tokens2.reset_index()
      tokens2.columns = ['Word','Frequency']
      DFs.append(tokens2)
      df = DFs[0]
      i=0
      for elem in DFs:
        df = pd.merge(df,elem,on="Word",how="outer")
      df.columns = [str(i) for i in range(len(df.columns))]
      df = df.drop('1',axis=1)
      df = df.replace(np.nan,0)
      df.set_index("0",inplace=True)
      df.columns = [str(i) for i in range(len(df.columns))]
      df = df.as_matrix()
    return df
  elif weight == "tf":
    for sent in sentences_cleaned:
      tokens = nltk.word_tokenize(sent)
      length = len(tokens)
      tokens2 = pd.DataFrame(tokens)
      tokens2.columns=['TF']
      tokens2 = pd.DataFrame(tokens2.TF.value_counts()/length)
      tokens2 = tokens2.reset_index()
      tokens2.columns = ['Word','TF']
      DFs.append(tokens2)
      df = DFs[0]
      i=0
      for elem in DFs:
        df = pd.merge(df,elem,on="Word",how="outer")
      df.columns = [str(i) for i in range(len(df.columns))]
      df = df.drop('1',axis=1)
      df = df.replace(np.nan,0)
      df.set_index("0",inplace=True)
      df.columns = [str(i) for i in range(len(df.columns))]
      df = df.as_matrix()
    return df
  elif weight == 'tf.idf':
    for sent in sentences_cleaned:
      tokens = nltk.word_tokenize(sent)
      length = len(tokens)
      tokens2 = pd.DataFrame(tokens)
      tokens2.columns=['TFIDF']
      tokens2 = pd.DataFrame(tokens2.TFIDF.value_counts()/length)
      tokens2 = tokens2.reset_index()
      tokens2.columns = ['Word','TFIDF']
      DFs.append(tokens2)
      df = DFs[0]
      i=0
      for elem in DFs:
        df = pd.merge(df,elem,on="Word",how="outer")
      df.columns = [str(i) for i in range(len(df.columns))]
      df = df.drop('1',axis=1)
      df = df.replace(np.nan,0)
      df.set_index("0",inplace=True)
      df.columns = [str(i) for i in range(len(df.columns))]
      num = len(df.columns)
      rows = []
      for index in df.index:
        den = np.count_nonzero(df.loc[index])
        idf = num/den
        idf = np.log(idf)
        row = df.loc[index]*idf
        rows.append(row)
    return pd.DataFrame(rows).as_matrix()

def SVD_weight(input,weight):
  df = weighting(input,weight)
  U, S, VT = np.linalg.svd(df, full_matrices=0)
  return pd.DataFrame(VT)

def ranking_sent(input,weight):
  matrix = SVD_weight(input,weight)
  score = {}
  for i in matrix.columns:
    score[i]=np.sqrt(np.sum(matrix[i]**2))
  return score

def LSA_summarize(input,num_of_sentences,weight="tf.idf"):
  ranking = ranking_sent(input,weight)
  sentences = sent_tokenize(input)
  if num_of_sentences > len(sentences):
    print("ERROR: There are only",len(sentences),"sentences in the text.")
  else:
    s = pd.DataFrame(pd.concat((pd.Series(sentences),pd.Series(ranking)),axis=1))
    s.columns = ['Sentence','Score']
    s = s.sort_values("Score",ascending = False)
    summary_sentences = [i for i in s['Sentence'][:num_of_sentences]]
    return ' '.join([str(elem) for elem in summary_sentences])


## 2. INDICATOR REPRESENTATION

# 2.1 GRAPH-BASED

#2.1.1 TextRank

#Load GloVe for text representation

!wget http://nlp.stanford.edu/data/glove.6B.zip

!unzip glove*.zip

# Extract word vectors

word_embeddings = {}
f = open('glove.6B.100d.txt', encoding='utf-8')
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    word_embeddings[word] = coefs
f.close()

#Function to get the summary

def summary(x,N,pretty=False):
  #Split into preprocessed and not preprocessed sentences
   sentences_cleaned = [text_preprocessing(y) for y in (sent_tokenize(x))]
   sentences = [y for y in (sent_tokenize(x))]
  #Text representation
   sentence_vectors = [] 
   for i in sentences_cleaned:
     if len(i) != 0:
       v = sum([word_embeddings.get(w, np.zeros((100,))) for w in i.split()])/(len(i.split())+0.001)
     else:
       v = np.zeros((100,))
     sentence_vectors.append(v) #IL PROBLEMA È QUI
   #Compute similarity matrix
   sim_mat = np.zeros([len(sentences), len(sentences)])
   for i in range(len(sentences)):
     for j in range(len(sentences)):
       if i != j:
         sim_mat[i][j] = cosine_similarity(sentence_vectors[i].reshape(1,100), sentence_vectors[j].reshape(1,100))[0,0]
   #Convert similarity matrix into a graph
   nx_graph = nx.from_numpy_array(sim_mat)
   scores = nx.pagerank(nx_graph)
   #Rank sentences
   ranked_sentences = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)
   #Select top N sentences
   summary=[]
   for i in range(N):
     summary.append(ranked_sentences[i][1])
   if pretty:
     return ' '.join([str(elem) for elem in summary]) #Return the readable text
   else:
     return summary #Return the list of summary sentences

# 2.1.2 Gensim (TextRank)

#Import summarizer from gensim package

from gensim.summarization.summarizer import summarize

# 2.1.3 PyTextRank (TextRank)

!pip install pytextrank

import logging
import pytextrank
import spacy
import sys

#Function for further analysis

def PTR(x,N=1):
  #Load a spaCy model, depending on language, scale, etc.
  nlp = spacy.load("en_core_web_sm")
  #Add PyTextRank into the spaCy pipeline
  tr = pytextrank.TextRank(logger=None)
  nlp.add_pipe(tr.PipelineComponent, name="textrank", last=True)
  doc = nlp(x)
  pytextrank_result = []
  for sent in doc._.textrank.summary(limit_phrases=15, limit_sentences=N):
    pytextrank_result.append(sent)
  return ' '.join([str(elem) for elem in pytextrank_result])

# 2.2 FEATURE-BASED

# 2.3.1 Luhn's Algorithm

#Function taking a word list and returning the set of keywords

def get_keywords(txt , min_ratio=0.05, max_ratio=0.5):
    txt = text_preprocessing(txt)
    length = len(nltk.word_tokenize(txt))
    count = {}    
    for word in nltk.word_tokenize(txt):
        count[word] = txt.count(word)
    keywords = []
    for word , cnt in count.items():
        percentage = count[word]*1.0 /length
        if percentage <= max_ratio and percentage >=min_ratio:
            keywords.append(word)
    #print("Found",100*len(keywords)/length,"% of keywords")
    return keywords

#Function returning the score of the sentence 
     
def get_sentence_weight (sentence , keywords):
    sen_list = nltk.word_tokenize(text_preprocessing(sentence))
    window_start = 0; window_end = -1;
    #Compute window start
    for i in range(len(sen_list)):
        if sen_list[i] in keywords:
            window_start = i
            break
    #Compute window end
    for i in range(len(sen_list) - 1 , 0 , -1) :
        if sen_list[i] in keywords:
            window_end = i
            break
    if window_start > window_end :
        return 0
    window_size = window_end - window_start + 1
    #Occurence of keywords in the sentence
    keywords_cnt = 0
    for w in sen_list :
        if w in keywords:
            keywords_cnt +=1
    #Return squared occurence of keywords normalized by window size
    score = keywords_cnt*keywords_cnt*1.0 / window_size
    return score

def Luhn_summarize(txt,num_of_sentences = 1):
  keywords_list = get_keywords(txt)
  score = {}
  for sentence in sent_tokenize(txt):
    score[sentence] = get_sentence_weight (sentence , keywords_list)
  #Convert the dictionary into DF
  Sentence = [i for i in score.keys()]
  Score = [i for i in score.values()]
  score = {'Sentence':Sentence,'Score':Score}
  score = pd.DataFrame(score)
  #Sort the DF
  ranking = score.sort_values("Score",ascending = False)
  summary_sentences = [i for i in ranking['Sentence'][:num_of_sentences]]
  return ' '.join([str(elem) for elem in summary_sentences])

# 2.3 DEEP LEARNING BASED

# 2.3.1 Extractive summarization with BERT Summarizer

!pip install spacy==2.1.3
!pip install transformers==2.2.0
!pip install bert-extractive-summarizer

#Import Bert summarizer
 
from summarizer import Summarizer

BERT = Summarizer()

def BERT_summarize(txt):
  result = BERT(txt)
  summary = ''.join(result)
  s = sent_tokenize(summary)
  return s[0]

# 2.3.2 Abstractive summarization with Sequence2Sequence LSTM model with Attention

from keras import backend as K
import gensim
from numpy import *
import numpy as np
import pandas as pd 
import re
from bs4 import BeautifulSoup
from keras.preprocessing.text import Tokenizer 
from keras.preprocessing.sequence import pad_sequences
from nltk.corpus import stopwords
from tensorflow.keras.layers import Input, LSTM, Embedding, Dense, Concatenate, TimeDistributed
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.utils import plot_model
import warnings
from sklearn.model_selection import train_test_split

#Function to preprocess the training e test feature set

def text_cleaner(text):
    newString = text.lower()
    newString = BeautifulSoup(newString, "lxml").text
    newString = re.sub(r'\([^)]*\)', '', newString)
    newString = re.sub('"','', newString)
    newString = ' '.join([contraction_mapping[t] if t in contraction_mapping else t for t in newString.split(" ")])    
    newString = re.sub(r"'s\b","",newString)
    newString = re.sub("[^a-zA-Z]", " ", newString) 
    tokens = [w for w in newString.split() if not w in stop_words]
    long_words=[]
    for i in tokens:
        if len(i)>=3:                  
            long_words.append(i)   
    return (" ".join(long_words)).strip()

#Function to preprocess the training and test target text

def summary_cleaner(text):
    newString = re.sub('"','', text)
    newString = ' '.join([contraction_mapping[t] if t in contraction_mapping else t for t in newString.split(" ")])    
    newString = re.sub(r"'s\b","",newString)
    newString = re.sub("[^a-zA-Z]", " ", newString)
    newString = newString.lower()
    tokens=newString.split()
    newString=''
    for i in tokens:
        if len(i)>1:                                 
            newString=newString+i+' '  
    return newString

#Reduce dataset dimensions

db = db[['Text','Summary']]
db.columns = ['text','summary']
contraction_mapping = contractions

#Apply preprocessing operations to the texts

cleaned_text = []
for t in db['text']:
    cleaned_text.append(text_cleaner(t))
db['text'] = cleaned_text
print("Text preprocessed.")

#Apply preprocessing operations to the summaries

cleaned_summary = []
for t in db['summary']:
    cleaned_summary.append(summary_cleaner(str(t)))
db['summary'] = cleaned_summary
db['summary'].replace('', np.nan, inplace=True)
print("Summary preprocessed.")

db.dropna(axis=0,inplace=True)
print("NA removed.")

#Add "START-END" and "sostok-eostok"

db['summary'] = db['summary'].apply(lambda x : '_START_ '+ x + ' _END_')
db['summary'] = db['summary'].apply(lambda x : 'sostok '+ x + ' eostok')

#Divide the corpus into training and validation set

x_tr,x_val,y_tr,y_val=train_test_split(np.array(db['text']),np.array(db['summary']),test_size=0.01,random_state=0,shuffle=True)

#Use tokenizer

x_tokenizer = Tokenizer() 
x_tokenizer.fit_on_texts(list(x_tr))

thresh=4
cnt=0
tot_cnt=0
freq=0
tot_freq=0

for key,value in x_tokenizer.word_counts.items():
    tot_cnt=tot_cnt+1
    tot_freq=tot_freq+value
    if(value<thresh):
        cnt=cnt+1
        freq=freq+value
    
print("% of rare words in vocabulary:",(cnt/tot_cnt)*100)
print("Total Coverage of rare words:",(freq/tot_freq)*100)

#Set maximum length

max_text_len=200 #Changeable
max_summary_len= 20

#Prepare a tokenizer for reviews on training data

x_tokenizer = Tokenizer(num_words=tot_cnt-cnt) 
x_tokenizer.fit_on_texts(list(x_tr))

#Convert text sequences into integer sequences (i.e one-hot encodeing all the words)

x_tr_seq    =   x_tokenizer.texts_to_sequences(x_tr) 
x_val_seq   =   x_tokenizer.texts_to_sequences(x_val)

#Padding zero upto maximum length

x_tr    =   pad_sequences(x_tr_seq,  maxlen=max_text_len, padding='post')
x_val   =   pad_sequences(x_val_seq, maxlen=max_text_len, padding='post')

#Size of vocabulary (+1 for padding token)

x_voc   =  x_tokenizer.num_words + 1

print("Size of vocabulary in X = {}".format(x_voc))

#Prepare a tokenizer for reviews on training data

y_tokenizer = Tokenizer()   
y_tokenizer.fit_on_texts(list(y_tr))

thresh=6

cnt=0
tot_cnt=0
freq=0
tot_freq=0

for key,value in y_tokenizer.word_counts.items():
    tot_cnt=tot_cnt+1
    tot_freq=tot_freq+value
    if(value<thresh):
        cnt=cnt+1
        freq=freq+value
    
print("% of rare words in vocabulary:",(cnt/tot_cnt)*100)
print("Total Coverage of rare words:",(freq/tot_freq)*100)

#Prepare a tokenizer for reviews on training data

y_tokenizer = Tokenizer(num_words=tot_cnt-cnt) 
y_tokenizer.fit_on_texts(list(y_tr))

#Convert text sequences into integer sequences (i.e one hot encode the text in Y)

y_tr_seq    =   y_tokenizer.texts_to_sequences(y_tr) 
y_val_seq   =   y_tokenizer.texts_to_sequences(y_val) 

#Padding zero upto maximum length

y_tr    =   pad_sequences(y_tr_seq, maxlen=max_summary_len, padding='post')
y_val   =   pad_sequences(y_val_seq, maxlen=max_summary_len, padding='post')

#Size of vocabulary

y_voc  =   y_tokenizer.num_words +1
print("Size of vocabulary in Y = {}".format(y_voc))

#Remove summaris with only START and END

ind=[]
for i in range(len(y_tr)):
    cnt=0
    for j in y_tr[i]:
        if j!=0:
            cnt=cnt+1
    if(cnt==2):
        ind.append(i)

y_tr=np.delete(y_tr,ind, axis=0)
x_tr=np.delete(x_tr,ind, axis=0)

ind=[]
for i in range(len(y_val)):
    cnt=0
    for j in y_val[i]:
        if j!=0:
            cnt=cnt+1
    if(cnt==2):
        ind.append(i)

y_val=np.delete(y_val,ind, axis=0)
x_val=np.delete(x_val,ind, axis=0)

#Create Attention Block

import tensorflow as tf
import os
from tensorflow.python.keras.layers import Layer
from tensorflow.python.keras import backend as K


class AttentionLayer(Layer):
    """
    This class implements Bahdanau attention (https://arxiv.org/pdf/1409.0473.pdf).
    There are three sets of weights introduced W_a, U_a, and V_a
     """

    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)

    def build(self, input_shape):
        assert isinstance(input_shape, list)
        # Create a trainable weight variable for this layer.

        self.W_a = self.add_weight(name='W_a',
                                   shape=tf.TensorShape((input_shape[0][2], input_shape[0][2])),
                                   initializer='uniform',
                                   trainable=True)
        self.U_a = self.add_weight(name='U_a',
                                   shape=tf.TensorShape((input_shape[1][2], input_shape[0][2])),
                                   initializer='uniform',
                                   trainable=True)
        self.V_a = self.add_weight(name='V_a',
                                   shape=tf.TensorShape((input_shape[0][2], 1)),
                                   initializer='uniform',
                                   trainable=True)

        super(AttentionLayer, self).build(input_shape)  # Be sure to call this at the end

    def call(self, inputs, verbose=False):
        """
        inputs: [encoder_output_sequence, decoder_output_sequence]
        """
        assert type(inputs) == list
        encoder_out_seq, decoder_out_seq = inputs
        if verbose:
            print('encoder_out_seq>', encoder_out_seq.shape)
            print('decoder_out_seq>', decoder_out_seq.shape)

        def energy_step(inputs, states):
            """ Step function for computing energy for a single decoder state """

            assert_msg = "States must be a list. However states {} is of type {}".format(states, type(states))
            assert isinstance(states, list) or isinstance(states, tuple), assert_msg

            """ Some parameters required for shaping tensors"""
            en_seq_len, en_hidden = encoder_out_seq.shape[1], encoder_out_seq.shape[2]
            de_hidden = inputs.shape[-1]

            """ Computing S.Wa where S=[s0, s1, ..., si]"""
            # <= batch_size*en_seq_len, latent_dim
            reshaped_enc_outputs = K.reshape(encoder_out_seq, (-1, en_hidden))
            # <= batch_size*en_seq_len, latent_dim
            W_a_dot_s = K.reshape(K.dot(reshaped_enc_outputs, self.W_a), (-1, en_seq_len, en_hidden))
            if verbose:
                print('wa.s>',W_a_dot_s.shape)

            """ Computing hj.Ua """
            U_a_dot_h = K.expand_dims(K.dot(inputs, self.U_a), 1)  # <= batch_size, 1, latent_dim
            if verbose:
                print('Ua.h>',U_a_dot_h.shape)

            """ tanh(S.Wa + hj.Ua) """
            # <= batch_size*en_seq_len, latent_dim
            reshaped_Ws_plus_Uh = K.tanh(K.reshape(W_a_dot_s + U_a_dot_h, (-1, en_hidden)))
            if verbose:
                print('Ws+Uh>', reshaped_Ws_plus_Uh.shape)

            """ softmax(va.tanh(S.Wa + hj.Ua)) """
            # <= batch_size, en_seq_len
            e_i = K.reshape(K.dot(reshaped_Ws_plus_Uh, self.V_a), (-1, en_seq_len))
            # <= batch_size, en_seq_len
            e_i = K.softmax(e_i)

            if verbose:
                print('ei>', e_i.shape)

            return e_i, [e_i]

        def context_step(inputs, states):
            """ Step function for computing ci using ei """
            # <= batch_size, hidden_size
            c_i = K.sum(encoder_out_seq * K.expand_dims(inputs, -1), axis=1)
            if verbose:
                print('ci>', c_i.shape)
            return c_i, [c_i]

        def create_inital_state(inputs, hidden_size):
            # We are not using initial states, but need to pass something to K.rnn funciton
            fake_state = K.zeros_like(inputs)  # <= (batch_size, enc_seq_len, latent_dim
            fake_state = K.sum(fake_state, axis=[1, 2])  # <= (batch_size)
            fake_state = K.expand_dims(fake_state)  # <= (batch_size, 1)
            fake_state = K.tile(fake_state, [1, hidden_size])  # <= (batch_size, latent_dim
            return fake_state

        fake_state_c = create_inital_state(encoder_out_seq, encoder_out_seq.shape[-1])
        fake_state_e = create_inital_state(encoder_out_seq, encoder_out_seq.shape[1])  # <= (batch_size, enc_seq_len, latent_dim

        """ Computing energy outputs """
        # e_outputs => (batch_size, de_seq_len, en_seq_len)
        last_out, e_outputs, _ = K.rnn(
            energy_step, decoder_out_seq, [fake_state_e],
        )

        """ Computing context vectors """
        last_out, c_outputs, _ = K.rnn(
            context_step, e_outputs, [fake_state_c],
        )

        return c_outputs, e_outputs

    def compute_output_shape(self, input_shape):
        """ Outputs produced by the layer """
        return [
            tf.TensorShape((input_shape[1][0], input_shape[1][1], input_shape[1][2])),
            tf.TensorShape((input_shape[1][0], input_shape[1][1], input_shape[0][1]))
        ]

pd.set_option("display.max_colwidth", 200)
warnings.filterwarnings("ignore") 
K.clear_session()

latent_dim = 300
embedding_dim=100

# Encoder

encoder_inputs = Input(shape=(max_text_len,))

#Embedding layer

enc_emb =  Embedding(x_voc, embedding_dim,trainable=True)(encoder_inputs)

#Encoder lstm 1

encoder_lstm1 = LSTM(latent_dim,return_sequences=True,return_state=True,dropout=0.4,recurrent_dropout=0.4)
encoder_output1, state_h1, state_c1 = encoder_lstm1(enc_emb)

#Encoder lstm 2

encoder_lstm2 = LSTM(latent_dim,return_sequences=True,return_state=True,dropout=0.4,recurrent_dropout=0.4)
encoder_output2, state_h2, state_c2 = encoder_lstm2(encoder_output1)

#Encoder lstm 3

encoder_lstm3=LSTM(latent_dim, return_state=True, return_sequences=True,dropout=0.4,recurrent_dropout=0.4)
encoder_outputs, state_h, state_c= encoder_lstm3(encoder_output2)

# Set up the decoder, using `encoder_states` as initial state

decoder_inputs = Input(shape=(None,))

#Embedding layer

dec_emb_layer = Embedding(y_voc, embedding_dim,trainable=True)
dec_emb = dec_emb_layer(decoder_inputs)

decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True,dropout=0.4,recurrent_dropout=0.2)
decoder_outputs,decoder_fwd_state, decoder_back_state = decoder_lstm(dec_emb,initial_state=[state_h, state_c])

# Attention layer

attn_layer = AttentionLayer(name='attention_layer')
attn_out, attn_states = attn_layer([encoder_outputs, decoder_outputs])

#Concat attention input and decoder LSTM output

decoder_concat_input = Concatenate(axis=-1, name='concat_layer')([decoder_outputs, attn_out])

#Dense layer

decoder_dense =  TimeDistributed(Dense(y_voc, activation='softmax'))
decoder_outputs = decoder_dense(decoder_concat_input)

#Define the model
 
model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

#Compile the model

model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy')

#Set and early stopping criterion

es = EarlyStopping(monitor='val_loss', mode='min', verbose=1,patience=2)

#Train the model

history=model.fit([x_tr,y_tr[:,:-1]], y_tr.reshape(y_tr.shape[0],y_tr.shape[1], 1)[:,1:] ,epochs=30,callbacks=[es],batch_size=128, validation_data=([x_val,y_val[:,:-1]], y_val.reshape(y_val.shape[0],y_val.shape[1], 1)[:,1:]))

#Visualize the learning process

plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='test')
plt.legend()
plt.show()

reverse_target_word_index=y_tokenizer.index_word
reverse_source_word_index=x_tokenizer.index_word
target_word_index=y_tokenizer.word_index

# Encode the input sequence to get the feature vector

encoder_model = Model(inputs=encoder_inputs,outputs=[encoder_outputs, state_h, state_c])

# Decoder setup
# Below tensors will hold the states of the previous time step

decoder_state_input_h = Input(shape=(latent_dim,))
decoder_state_input_c = Input(shape=(latent_dim,))
decoder_hidden_state_input = Input(shape=(max_text_len,latent_dim))

# Get the embeddings of the decoder sequence

dec_emb2= dec_emb_layer(decoder_inputs) 

# To predict the next word in the sequence, set the initial states to the states from the previous time step

decoder_outputs2, state_h2, state_c2 = decoder_lstm(dec_emb2, initial_state=[decoder_state_input_h, decoder_state_input_c])

#Attention inference

attn_out_inf, attn_states_inf = attn_layer([decoder_hidden_state_input, decoder_outputs2])
decoder_inf_concat = Concatenate(axis=-1, name='concat')([decoder_outputs2, attn_out_inf])

#A dense softmax layer to generate prob dist. over the target vocabulary

decoder_outputs2 = decoder_dense(decoder_inf_concat) 

# Final decoder model

decoder_model = Model(
    [decoder_inputs] + [decoder_hidden_state_input,decoder_state_input_h, decoder_state_input_c],
    [decoder_outputs2] + [state_h2, state_c2])

def decode_sequence(input_seq):
    # Encode the input as state vectors.
    e_out, e_h, e_c = encoder_model.predict(input_seq)
    
    # Generate empty target sequence of length 1.
    target_seq = np.zeros((1,1))
    
    # Populate the first word of target sequence with the start word.
    target_seq[0, 0] = target_word_index['sostok']

    stop_condition = False
    decoded_sentence = ''
    while not stop_condition:
      
        output_tokens, h, c = decoder_model.predict([target_seq] + [e_out, e_h, e_c])

        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_token = reverse_target_word_index[sampled_token_index]
        
        if(sampled_token!='eostok'):
            decoded_sentence += ' '+sampled_token

        # Exit condition: either hit max length or find stop word.
        if (sampled_token == 'eostok'  or len(decoded_sentence.split()) >= (max_summary_len-1)):
            stop_condition = True

        # Update the target sequence (of length 1).
        target_seq = np.zeros((1,1))
        target_seq[0, 0] = sampled_token_index

        # Update internal states
        e_h, e_c = h, c

    return decoded_sentence

def seq2summary(input_seq):
    newString=''
    for i in input_seq:
        if((i!=0 and i!=target_word_index['sostok']) and i!=target_word_index['eostok']):
            newString=newString+reverse_target_word_index[i]+' '
    return newString

def seq2text(input_seq):
    newString=''
    for i in input_seq:
        if(i!=0):
            newString=newString+reverse_source_word_index[i]+' '
    return newString

## 3. EVALUATION

# Human quality evaluation

#We will take 25 summaries made by each method and evaluate them with a score from 0 to 3 #in terms of effectiveness and utility, namely the ability of reporting the main opinion #expressed by the Amazon user about the given item. The score will be 
#- **0**, if summary is completely non understandable
#- **1**, if summary is clear but return other concepts or the opposite idea with respect #to the original text
#- **2**, if summary is well comprehensible and provide an information, but this #information does not sum up effectively the content of the text
#- **3**, if summary is perfectly comprehensible and provide the right information about #the main content of the text

#The final evaluation will be computed as the average score over the same reviews.