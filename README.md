# Pipeline Academy - Project Outline
## Davide Posillipo

### Abstract
In this project I want to focus on textual data extracted from a website via web scraping. The goal is to set up a data infrastructure that includes a scraper, a database for the extracted data, a machine learning engine for NLP tasks and a front-end for interactive analysis of the data. The idea is to provide a *power tool* for users with domain knowledge. 

### Data
The data source is the online library provided by the Jehovas's Witnesses organization (JW). JW is an american religion spread all over the world. They provide for public usage an interactive library that contains part of the textual material that they created since 1950. The library is hosted at this address: https://wol.jw.org/en/wol/h/r1/lp-e. 

JW are active since 1870, so a big chunk fo the textual documents created by JW is not available in the online library. This textual data not available in the online library could be retrieved and ingested with different data sources (there are on the market some collections in DVD format containing the full library since the origin). Depending on the progression of the project and time availability, I may extend the scope of the project to these additional sources. 

### Goal
The goal is to provide a *power tool* for users interested in the history of JW. Through NLP, the user can explore the evolution and the doctrine of this religion in a way that is impossible simply using the original library. 

### Potential users
Sociologist of religions, historians of religions, former JWs. 

### Infrastructure
The main components of the infrastructure should be:

* A web scraper
* A non-sql database to store the scraped data
* A machine learning engine that runs NLP task on the scraped data
* An interactive front-end with visualizations and the results of the NLP tasks

These components should be hosted on the cloud (AWS?) and the interactive front-end should be available as web service.

#### About the NLP engine
Given the focus of Pipeline Academy on Data Engineer, I will spend more time in creating a robust data infrastructure than in creating a cool NLP engine. I will provide a baseline of standard techniques and leave for future development more advanced stuff. The diea is to create a *modular* product that will make easy to deploy additional NLP components. Potentially, an API could be provided so that other developers can use the tool in order to perform further NLP analyses. 

### Challenges - or what could go wrong
* Scraping too complex
* difficulties in setting up a regular scraping
* setting up a web service with frontend - never done before
* not enough time for good quality NLP, but this is not a show stopper
