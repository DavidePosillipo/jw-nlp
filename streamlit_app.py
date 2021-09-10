import streamlit as st
import os
import spacy
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import pickle
import requests
from jwnlp.nlp.summarization.summarize_article import summarize_article
import psycopg2

# Needed to print the wordcloud in the easiest way
st.set_option('deprecation.showPyplotGlobalUse', False)

st.title("JW-NLP")
st.write("First test with streamlit")

### CONNECTING TO DB
conn = psycopg2.connect("dbname=jwnlp user=admin")
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM watchtowers_articles")
num_of_wt = cur.fetchall()[0][0]

st.write("Number of scraped articles: ", num_of_wt) 

### WORDCLOUD
sp = spacy.load('en_core_web_sm')

cur.execute("""
    SELECT data->'title' FROM watchtowers_articles WHERE data->'article_id' = '"1997004"';
    """)
article_title = cur.fetchall()[0][0]

cur.execute("""
            SELECT
                data
            FROM
                watchtowers_articles
            WHERE
                data->'article_id' = '"1997004"'
            ;
            """)
article_dict = cur.fetchall()[0][0]
    
paragraphs = {int(k[1:]): v for (k,v) in article_dict['paragraphs'].items()}
total_text = '\n'.join([p[1] for p in sorted(paragraphs.items())])

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
st.write(f"This is the wordcloud of the adjectives for the article {article_title}")
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
st.write(f"This is the wordcloud of the nouns for the article {article_title}")
st.pyplot()

# text summarization
summary = summarize_article(article_dict, max_length=450)
st.write(f"This is a summary of the article {article_title} made with the T5 deep learning model")
summary
