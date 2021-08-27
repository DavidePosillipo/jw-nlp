from jwnlp.scraper.wt_scraper_new import wtScraper
from jwnlp.parser.article_parser import ArticleParser
#from jwnlp.scraper.async_utils import fetch, extract
import json
import pickle
import aiohttp
import asyncio
from pathlib import Path

if __name__ == '__main__':

    # async functions 
    #TODO put them in a different module (is it possible?)
    async def fetch(url, session):
         async with session.get(url) as response: 
             return await response.text() 
    
    
    async def extract(extracting_function, target_urls, save_raw_response=False, **kwargs):
        tasks = []
        async with aiohttp.ClientSession() as session:
            for url in target_urls.values():
                task = asyncio.ensure_future(fetch(url, session))
                tasks.append(task)
    
            pages_contents = await asyncio.gather(*tasks)

            if save_raw_response:
                to_save = dict(zip(target_urls.values(), pages_contents))
                for page_url, page_content in to_save.items():
                    file_name = page_url.split('/')[-1]
                    scraper.dump_scraped_page(folder=kwargs['folder'], response=page_content, file_name=file_name)

            extracted_elements = [extracting_function(page) for page in pages_contents]
            output_dict = dict(zip(target_urls.keys(), extracted_elements))
                
            return(output_dict)
    
    language = 'en'
    scraper = wtScraper(language)

    links_by_year = scraper.get_years() 

    #### STEP 1 ####
    # Retrieving the issues links for the WT up to 2007

    links_by_year_pre_2008 = {y: l for (y, l) in links_by_year.items() if y<2008}
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(extract(scraper.get_issues_links, links_by_year_pre_2008))
    # {year: {issue_id: link, ...}, ...}
    issues_links_pre_2008 = loop.run_until_complete(future)


    #### STEP 2 ####
    # Retrieving the issues links for the WT from 2008

    # A link for each year, but not to the issue, but to the study-public fork
    links_by_year_from_2008 = {y: l for (y, l) in links_by_year.items() if y>=2008}

    ## STEP 2.1 ##
    # Retrieving the different links for study and public versions
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(extract(scraper.get_public_or_study, links_by_year_from_2008))
    # {year: {month: [link_to_public, link_to_study], ...}, ...}
    study_or_public_links = loop.run_until_complete(future)
 
    public_links = {year: links[0] for (year, links) in study_or_public_links.items()}
    study_links = {year: links[1] for (year, links) in study_or_public_links.items()}

    ## STEP 2.2 ##
    # Retrieving the issues links for both study and public editions      

    # Study links 
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(extract(scraper.get_issues_links, study_links))
    # {year: {issue_id: link, ...}, ...}
    issues_links_study_from_2008 = loop.run_until_complete(future)

    # Public links 
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(extract(scraper.get_issues_links, public_links))
    # {year: {issue_id: link, ...}, ...}
    issues_links_public_from_2008 = loop.run_until_complete(future)


    #### STEP 3 ####
    # Retrieve the articles links from each issue
    # {year: {issue_id: {article_title: article_url, ...}, ...}, ...}
    articles_links_pre_2008 = dict()
    articles_links_from_2008_study = dict()
    articles_links_from_2008_public = dict()
   
    ## STEP 3.1 ##
    # Pre-2008 articles' links
    for year, year_issues_dict in issues_links_pre_2008.items():
        # For debug
        #if year==2003:
        print("Getting articles links for year", year)
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(extract(scraper.get_articles_links_by_title, year_issues_dict)) 
        # {issue_id: {article_title: article_url, ...}, ...}
        this_year_articles_links = loop.run_until_complete(future)

        articles_links_pre_2008[year] = this_year_articles_links       
 
    ## STEP 3.2 ##
    # From-2008 articles' links

    # Study version
    for year, year_issues_dict in issues_links_study_from_2008.items():
        print("Getting articles links for study edition, year", year)
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(extract(scraper.get_articles_links_by_title, year_issues_dict))
        # {issue_id: {article_title: article_url, ...}, ...}
        this_year_articles_links = loop.run_until_complete(future)

        articles_links_from_2008_study[year] = this_year_articles_links

    # Public version
    for year, year_issues_dict in issues_links_public_from_2008.items():
        print("Getting articles links for public edition, year", year)
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(extract(scraper.get_articles_links_by_title, year_issues_dict))
        # {issue_id: {article_title: article_url, ...}, ...}
        this_year_articles_links = loop.run_until_complete(future)

        articles_links_from_2008_public[year] = this_year_articles_links


    #### STEP 4 ####
    # Extracting text from each article and saving them to json 
    parser = ArticleParser(publication="watchtower")

    ## STEP 4.1 ##
    # Articles pre-2008

    # Dictionary structure from where we start
    # {year: {issue_id: {article_title: article_url, ...}, ...}, ...}
    for year in articles_links_pre_2008.keys():
        print("Extracting articles for year", year)
        this_year_issues = articles_links_pre_2008[year]

        for issue in this_year_issues.keys():

            # Creating the output folders if needed
            #TODO to put in try/catch
            output_folder_raw = "./data/raw/generic/" + str(year) + "/" + issue
            Path(output_folder_raw).mkdir(parents=True, exist_ok=True)
            output_folder_parsed = "./data/parsed/generic/" + str(year) + "/" + issue
            Path(output_folder_parsed).mkdir(parents=True, exist_ok=True)
           
            # {article_title: article_url, ...} 
            this_issue_articles = this_year_issues[issue]

            loop = asyncio.get_event_loop()
            # in this case, saving the text response of page to file
            future = asyncio.ensure_future(extract(parser.extract_paragraphs_from_article, this_issue_articles, save_raw_response=True, folder=output_folder_raw))
            # {article_title: {paragraph_id, paragraph(bs4), ...}, ...}
            this_issue_articles_paragraphs = loop.run_until_complete(future)
            # same structure, but with the cleaned text instead
            this_issue_articles_paragraphs_text = {article: parser.process_paragraphs(paragraphs) for (article, paragraphs) in this_issue_articles_paragraphs.items()} 

            # Saving the articles as json files
            for article_title, article_text in this_issue_articles_paragraphs_text.items():
                article_url = this_issues_articles[article_title]
                parser.save_article_to_json(
                                             output_folder = output_folder_parsed,
                                             year = year,
                                             edition = "Generic",
                                             issue_id = issue,
                                             paragraphs = article_text,
                                             url = article_url,
                                             language = language,
                                             title = article_title
                                            )
                
             
  
    ## STEP 4.2 ##
    # Articles from 2008 - study edition

    # Dictionary structure from where we start
    # {year: {issue_id: {article_title: article_url, ...}, ...}, ...}
    for year in articles_links_from_2008_study.keys():
        print("Extracting articles (Study Edition) for year", year)
        this_year_issues = articles_links_from_2008_study[year]

        for issue in this_year_issues.keys():

            # Creating the output folders if needed
            #TODO to put in try/catch
            output_folder_raw = "./data/raw/study/" + str(year) + "/" + issue
            Path(output_folder_raw).mkdir(parents=True, exist_ok=True)
            output_folder_parsed = "./data/parsed/study/" + str(year) + "/" + issue
            Path(output_folder_parsed).mkdir(parents=True, exist_ok=True)
           
            # {article_title: article_url, ...} 
            this_issue_articles = this_year_issues[issue]

            loop = asyncio.get_event_loop()
            # in this case, saving the text response of page to file
            future = asyncio.ensure_future(extract(parser.extract_paragraphs_from_article, this_issue_articles, save_raw_response=True, folder=output_folder_raw))
            # {article_title: {paragraph_id, paragraph(bs4), ...}, ...}
            this_issue_articles_paragraphs = loop.run_until_complete(future)
            # same structure, but with the cleaned text instead
            this_issue_articles_paragraphs_text = {article: parser.process_paragraphs(paragraphs) for (article, paragraphs) in this_issue_articles_paragraphs.items()} 

            # Saving the articles as json files
            for article_title, article_text in this_issue_articles_paragraphs_text.items():
                article_url = this_issues_articles[article_title]
                parser.save_article_to_json(
                                             output_folder = output_folder_parsed,
                                             year = year,
                                             edition = "Study",
                                             issue_id = issue,
                                             paragraphs = article_text,
                                             url = article_url,
                                             language = language,
                                             title = article_title
                                            )
     

    ## STEP 4.3 ##
    # Articles from 2008 - public edition

    # Dictionary structure from where we start
    # {year: {issue_id: {article_title: article_url, ...}, ...}, ...}
    for year in articles_links_from_2008_public.keys():
        print("Extracting articles (Public Edition) for year", year)
        this_year_issues = articles_links_from_2008_public[year]

        for issue in this_year_issues.keys():

            # Creating the output folders if needed
            #TODO to put in try/catch
            output_folder_raw = "./data/raw/public/" + str(year) + "/" + issue
            Path(output_folder_raw).mkdir(parents=True, exist_ok=True)
            output_folder_parsed = "./data/parsed/public/" + str(year) + "/" + issue
            Path(output_folder_parsed).mkdir(parents=True, exist_ok=True)
           
            # {article_title: article_url, ...} 
            this_issue_articles = this_year_issues[issue]

            loop = asyncio.get_event_loop()
            # in this case, saving the text response of page to file
            future = asyncio.ensure_future(extract(parser.extract_paragraphs_from_article, this_issue_articles, save_raw_response=True, folder=output_folder_raw))
            # {article_title: {paragraph_id, paragraph(bs4), ...}, ...}
            this_issue_articles_paragraphs = loop.run_until_complete(future)
            # same structure, but with the cleaned text instead
            this_issue_articles_paragraphs_text = {article: parser.process_paragraphs(paragraphs) for (article, paragraphs) in this_issue_articles_paragraphs.items()} 

            # Saving the articles as json files
            for article_title, article_text in this_issue_articles_paragraphs_text.items():
                article_url = this_issues_articles[article_title]
                parser.save_article_to_json(
                                             output_folder = output_folder_parsed,
                                             year = year,
                                             edition = "Public",
                                             issue_id = issue,
                                             paragraphs = article_text,
                                             url = article_url,
                                             language = language,
                                             title = article_title
                                            )
            
