import streamlit as st
import os
import spacy
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import pickle

st.title("JW-NLP")

st.write("First test with streamlit")

num_of_wt = sum([len(files) for r, d, files in os.walk('./data/parsed/')])

st.write("Number of scraped wt: ", num_of_wt) 

### WORDCLOUD
sp = spacy.load('en_core_web_sm')

with open("./data/parsed/array_of_docs_to_index.pkl", "rb") as f:
    wts = pickle.load(f)

total_text = "".join([article['paragraphs'] for article in wts if article['year']==2010 and article['issue_id']=='january-15'])

sp_total_text = sp(total_text)

# Keeping only adjectives; lower case
adjectives = ''
for word in sp_total_text:
    if word.pos_ in ['ADJ']:
        adjectives = " ".join((adjectives, word.text.lower()))

wordcloud_a = WordCloud(stopwords=STOPWORDS).generate(adjectives)

plt.imshow(wordcloud_a, interpolation='bilinear')
plt.axis("off")
plt.show()
st.pyplot()

# Keeping only nouns; lower case
nouns = ''
for word in sp_total_text:
    if word.pos_ in ['NOUN']:
        nouns = " ".join((nouns, word.text.lower()))

wordcloud_n = WordCloud(stopwords=STOPWORDS).generate(nouns)

plt.imshow(wordcloud_n, interpolation='bilinear')
plt.axis("off")
plt.show()
st.pyplot()
