from jwnlp.scraper.wt_scraper_new import wtScraper
#from jwnlp.scraper.async_utils import fetch, extract
import json
import pickle
import aiohttp
import asyncio

if __name__ == '__main__':

    # async functions 
    #TODO put them in a different module (is it possible?)
    async def fetch(url, session):
         async with session.get(url) as response: 
             return await response.text() 
    
    
    async def extract(extracting_function, target_urls):
        tasks = []
        async with aiohttp.ClientSession() as session:
            for url in target_urls.values():
                task = asyncio.ensure_future(fetch(url, session))
                tasks.append(task)
    
            pages_contents = await asyncio.gather(*tasks)
            extracted_elements = [extracting_function(page) for page in pages_contents]
            output_dict = dict(zip(target_urls.keys(), extracted_elements))
                
            return(output_dict)
    

    scraper = wtScraper('en')

    links_by_year = scraper.get_years() 
    #links_by_month = {year: scraper.get_links_by_month(link) for (year,link) in links_by_year.items()}

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

    # Due to naming convention change in 2016
#    public_links_pre_2016 = {y: l for (y, l) in public_links.items() if y<2016}
#    public_links_from_2016 = {y: l for (y, l) in public_links.items() if y>=2016}
#
#    study_links_pre_2016 = {y: l for (y, l) in study_links.items() if y<2016}
#    study_links_from_2016 = {y: l for (y, l) in study_links.items() if y>=2016}
#
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

    # Study from 2016
    #loop = asyncio.get_event_loop()
    #future = asyncio.ensure_future(extract(scraper.get_wt_links_by_month_post_2015, study_links_from_2016))
    ## {year: {month: link, ...}, ...}   
    #issues_links_study_from_2016 = loop.run_until_complete(future)

    ## Public from 2016
    #loop = asyncio.get_event_loop()
    #future = asyncio.ensure_future(extract(scraper.get_wt_links_by_month_post_2015, public_links_from_2016))
    ## {year: {month: link, ...}, ...}
    #issues_links_public_from_2016 = loop.run_until_complete(future)


    #### STEP 3 ####
    # Retrieve the articles links from each issue
    # {year: {issue_id: {article_title: article_url, ...}, ...}, ...}
    articles_links_pre_2008 = dict()
    articles_links_post_2008_study = dict()
    articles_links_post_2008_public = dict()
   
    ## STEP 3.1 ##
    # Pre-2008 articles' links
    for year, year_issues_dict in issues_links_pre_2008.items():
        # For debug
        if year==2003:
            print("Getting articles links for year", year)
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(extract(scraper.get_articles_links_by_title, year_issues_dict)) 
            # {issue_id: {article_title: article_url, ...}, ...}
            this_year_articles_links = loop.run_until_complete(future)

            articles_links_pre_2008[year] = this_year_articles_links       
 
    print(articles_links_pre_2008[2003]) 
