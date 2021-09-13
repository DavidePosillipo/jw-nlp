from jwnlp.scraper.wt_scraper import wtScraper
from jwnlp.parser.article_parser import ArticleParser
from jwnlp.utils.flatten_dict import flatten
import json
import pickle
import aiohttp
import asyncio
from pathlib import Path
import logging
import traceback
import sys

#TODO handle better the combinations of starting and final year, or put assert at least

def scrape_wt_batch(language: str, starting_year=1950, final_year=2021):
    '''
    Execute a full scraping of the JW website, in order to retrieve 
    all the available Watchtower issues, for the given language. 
    It uses async calls that currently work only OUTSIDE of a VPN.

    It creates a library on the filesystem with each article from each 
    issue saved both as a raw page (in txt) and as parsed JSON file.

    CAVEAT: it works only if starting_year < 2008 and final_year > 2008

    Args:
        language (str): The desired language of the issues that must be scraped
        starting_year (int): The first year of the collection to be scraped
        final_year (int): The last year of the collection to be scraped

    Returns:
        None   
    '''
    
    logging.basicConfig(handlers=[
                                  logging.FileHandler("./temp/scraping.log"),
                                  logging.StreamHandler()
                                  ],
                        level=logging.DEBUG, 
                        format='%(asctime)s %(message)s', 
                        datefmt='%m/%d/%Y %I:%M:%S %p')

    logger = logging.getLogger(__name__)
   
    non_scraped_articles_dict = dict()
 
    # async functions 
    #TODO put them in a different module (is it possible?)
    async def fetch(url, session):
        try:
            async with session.get(url) as response: 
                return await response.text() 
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Error {e} encountered for url {url}")
    
    
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


    async def extract_articles(year: int, extracting_function, target_urls: dict):
        """
        Extract the paragraphs from the articles links in the input dictionary. 
        It saves the articles pages as txt file (raw).

        Args:
            extracting_function (fun): the function with the instructions for 
            the extraction of the paragraphs
            target_urls (dict): {issueId_articleTitle: article_link}
        
        Returns:
            dict: {issueId_articleTitle(str): paragraphs(dict)}, a dictionary 
            with a dictionary of paragraphs for each entry 
        """
        tasks = []
        connector = aiohttp.TCPConnector(limit_per_host=100)
        async with aiohttp.ClientSession(connector=connector) as session:
            for url in target_urls.values():
                task = asyncio.ensure_future(fetch(url, session))
                tasks.append(task)

            pages_contents = await asyncio.gather(*tasks)

            output_dict = dict()
            global non_scraped_articles_dict

            # Processing each article
            for key, page in zip(target_urls.keys(), pages_contents):
                article_url = target_urls[key]
                article_id = article_url.split('/')[-1]
                raw_file_name = article_id + '.txt'

                issue = key.split('_')[0]
                
                # Creating the output folders if needed
                output_folder_raw = "./data/raw/generic/" + str(year) + "/" + issue
                Path(output_folder_raw).mkdir(parents=True, exist_ok=True)

                # Saving raw page
                try:
                    scraper.dump_scraped_page(output_folder_raw, page, raw_file_name)
                except Exception as e:
                    logger.error(f"An article could not be scraped. The article is {article_id}, link {article_url}.")
                    non_scraped_articles_dict[article_id] = {"article_id": article_id, "url": article_url, "error": traceback.format_exception(*sys.exc_info())}
                    # go to the next article and stop processing this faulty one
                    continue 

                # Parsing the articles 
                try:
                    parsed_article = extracting_function(page)
                    output_dict[key] = parsed_article
                except Exception as e:
                    logger.error(f"An error occurred while processing the page {target_urls[key]}. The error is {traceback.format_exception(*sys.exc_info())}")
                    non_scraped_articles_dict[article_id] = {"article_id": article_id, "url": article_url, "error": traceback.format_exception(*sys.exc_info())}
                
            return output_dict

    
    scraper = wtScraper(language)

    logger.info("STEP 0 - Scraping the years")
    links_by_year = scraper.get_years() 

    #### STEP 1 ####
    # Retrieving the issues links for the WT up to 2007
    logger.info("STEP 1 - Retrieving issues links")
    links_by_year_pre_2008 = {y: l for (y, l) in links_by_year.items() if y<2008 and y>=starting_year}
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(extract(scraper.get_issues_links, links_by_year_pre_2008))
    # {year: {issue_id: link, ...}, ...}
    issues_links_pre_2008 = loop.run_until_complete(future)


    #### STEP 2 ####
    # Retrieving the issues links for the WT from 2008
    logger.info("STEP 2 - Retrieving issues links post 2007")
    # A link for each year, but not to the issue, but to the study-public fork
    links_by_year_from_2008 = {y: l for (y, l) in links_by_year.items() if y>=2008 and y<=final_year}

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
    logger.info("STEP 3 - Retrieving articles links")
    # Retrieve the articles links from each issue
    # {year: {issue_id: {article_title: article_url, ...}, ...}, ...}
    articles_links_pre_2008 = dict()
    articles_links_from_2008_study = dict()
    articles_links_from_2008_public = dict()
   
    ## STEP 3.1 ##
    # Pre-2008 articles' links
    for year, year_issues_dict in issues_links_pre_2008.items():
        logger.info(f"Getting articles links for year {year}")
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(extract(scraper.get_articles_links_by_title, year_issues_dict)) 
        # {issue_id: {article_title: article_url, ...}, ...}
        this_year_articles_links = loop.run_until_complete(future)

        articles_links_pre_2008[year] = this_year_articles_links       
 
    ## STEP 3.2 ##
    # From-2008 articles' links

    # Study version
    for year, year_issues_dict in issues_links_study_from_2008.items():
        logger.info(f"Getting articles links for study edition, year {year}")
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(extract(scraper.get_articles_links_by_title, year_issues_dict))
        # {issue_id: {article_title: article_url, ...}, ...}
        this_year_articles_links = loop.run_until_complete(future)

        articles_links_from_2008_study[year] = this_year_articles_links

    # Public version
    for year, year_issues_dict in issues_links_public_from_2008.items(): 
        logger.info(f"Getting articles links for public edition, year {year}")
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(extract(scraper.get_articles_links_by_title, year_issues_dict))
        # {issue_id: {article_title: article_url, ...}, ...}
        this_year_articles_links = loop.run_until_complete(future)

        articles_links_from_2008_public[year] = this_year_articles_links


    #### STEP 4 ####
    logger.info("STEP 4 - Extracting articles and saving them to JSON")
    # Extracting text from each article and saving them to json 
    parser = ArticleParser(publication="watchtower")

    def step_4(non_flat_dict: dict, edition: str, year: int):
        # Dictionary structure from where we start
        # {issue_id: {article_title: article_url, ...}, ...}
        # Flattening the dict -> {issueId_articleTitle: article_url} 
        flat_dict = flatten(non_flat_dict)

        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(
                    extract_articles(
                        year,
                        parser.extract_paragraphs_from_article,
                        flat_dict 
                        )
                    )
        parsed_articles = loop.run_until_complete(future)

        # Saving the articles as json files
        for key, parsed_article in parsed_articles.items():
            article_url = flat_dict[key]
            
            issue = key.split('_')[0]
            article_title = key.split('_')[1] 
            
            output_folder_parsed = "./data/parsed/" + edition + "/" + str(year) + "/" + issue
            Path(output_folder_parsed).mkdir(parents=True, exist_ok=True)

            # Extracting text from the paragraphs
            paragraphs = parser.process_paragraphs(parsed_article)
 
            parser.save_article_to_json(
                                        output_folder = output_folder_parsed,
                                        year = year,
                                        edition = edition,
                                        issue_id = issue,
                                        paragraphs = paragraphs,
                                        url = article_url,
                                        language = language,
                                        title = article_title
                                       )
                    
    logger.info("STEP 4.1 - pre 2008")
    for year, issues_articles_dict in articles_links_pre_2008.items():
        logger.info(f"Extracting articles for the year {year}")
        step_4(issues_articles_dict, "generic", year)

    logger.info("STEP 4.2 - from 2008 Public")
    for year, issues_articles_dict in articles_links_from_2008_public.items():
        logger.info(f"Extracting (public) articles for the year {year}")
        step_4(issues_articles_dict, "public", year)

    logger.info("STEP 4.3 - from 2008 Study")
    for year, issues_articles_dict in articles_links_from_2008_study.items():
        logger.info(f"Extracting (study) articles for the year {year}")
        step_4(issues_articles_dict, "study", year)


    with open("./temp/non_scraped_articles.pkl", "wb") as f:
        pickle.dump(non_scraped_articles_dict, f)
