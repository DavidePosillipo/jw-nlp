# JW-NLP: an AI-powered tool to explore the JW.org literature
## Davide Posillipo (as portfolio project for Pipeline Academy)

### Abstract
In this project I want to focus on textual data extracted from a website via web scraping. The goal is to set up a data infrastructure that includes a scraper, a database for the extracted data, a machine learning engine for NLP tasks and a front-end for interactive analysis of the data. The idea is to provide a *power tool* for users with domain knowledge. 

### A caveat
The data product described here is meant to be built and deployed with a specific corpus of documents, but its structure will be the same if the author will decide to deploy it first with a subset of Reddit and other forums posts related to the same theme. The author imagines to integrate both sources anyway at some point. 

### Data
The data source is the online library provided by the Jehovas's Witnesses organization (JW). JW is an american religion spread all over the world. They provide for public usage an interactive library that contains part of the textual material that they created since 1950. The library is hosted at this address: https://wol.jw.org/en/wol/h/r1/lp-e. 

JW are active since 1870, so a big chunk fo the textual documents created by JW is not available in the online library. This textual data not available in the online library could be retrieved and ingested with different data sources (there are on the market some collections in DVD format containing the full library since the origin). Depending on the progression of the project and time availability, I may extend the scope of the project to these additional sources. 

### Goal
The goal is to provide a *power tool* for users interested in the history of JW. Through NLP, the user can explore the evolution and the doctrine of this religion in a way that is impossible simply using the original library. 

### Potential users
Sociologist of religions, historians of religions, former JWs. 

### Infrastructure
The main components of the infrastructure should be:

* web scraper
* S3 bucket for data dump
* non-sql database to store the parsed data
* transformer module
* indexing module and search engine
* machine learning engine that runs NLP tasks on the scraped data
* interactive front-end with visualizations and the results of the NLP tasks

These components should be hosted on the cloud (AWS) and the interactive front-end should be available as web service.

#### Web Scraper
The web scraper is a Python application based on Beatiful Soup. Its responsabilities are:

* connect to the source website
* retrieve the desired HTML files
* return a list of unparsed text elements

#### S3 Bucket for data dump
The web scraper returns a list on unparsed text elements; these are dumped in the S3 bucket.

#### Transformer module
A python module that is in charge of:

* extract and clean the text retrieved by the scraper
* organize the content in a shape usable by the search engine and the NLP libraries
* find the links between pubblications and store them in a suitable data structure
* store the parsed data in the non-sql database

#### Indexing module and search engine
This module builds an index of the documents corpus and takes care of the creation of a retrieval function for the search engine. 

For this module the application leverages on Pyserini (that is built on top of Lucene). A possible retrieval function is the BM-25. 

[OPTIONAL] A re-ranking module based on deep learning refines the search results (similarly as what happens in [this search engine](http://covidex.ai/). Its infrastructure is described in [this](https://aclanthology.org/2020.sdp-1.5/) paper and represents more or less the state of the art of Information Retrieval based on Deep Learning. 

#### Machine Learning Engine
It performs analysis triggered by the user interaction through the UI. For this reason, it is deployed as API on AWS. 

Example of analyses:
* time series of the occurence of a specific term/concept
* sentyment analysis of a specific publication 
* ...

##### About the Machine Learning Engine
Given the focus of Pipeline Academy on Data Engineering, the first version of the tool will contain vanilla machine learning. I will provide a baseline of standard techniques and leave for future development more advanced stuff. The idea is to create a *modular* product that will make easy to deploy additional NLP components. 

#### Interactive Frontend
A front-end built with Streamlit that let the user:
* submit queries to the search engine (corpus exploration)
* access to the analyses provided by the Machine Learning Engine

### Deployment
The application is deployed on AWS with Prefect. The ETL steps are executed each month, in order to retrieve the last issues of the publications. 

### CD/CI
Integration with Github Actions. 

### Serving data to other machines
[IF FEASIBLE] An API is provided to let other applications download the results of the analyses.
