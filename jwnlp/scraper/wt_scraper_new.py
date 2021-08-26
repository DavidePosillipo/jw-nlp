import requests
import re
from bs4 import BeautifulSoup
import aiohttp
import asyncio

class wtScraper:

    def __init__(self, language):
        self.language = language
        self.homepage = 'https://wol.jw.org/' + self.language + '/wol/library/r1/lp-e/all-publications/watchtower'
        self.root = 'https://wol.jw.org'

    
    def get_years(self):
        '''
        Access the mainpage and retrieve the links for each single
        year of WT
        '''
        scraped_homepage = self.scrape_page(self.homepage) 
        parsed_page = self.parse_page(scraped_homepage)
     
        only_links = self.extract_links(parsed_page)
        
        search_years = re.compile(r"(?<=-)[0-9]+")
        years = [int(search_years.search(x).group()) for x in only_links]
        wt_for_years_dict = dict(zip(years, only_links))
    
        return wt_for_years_dict

    
    def get_wt_links_by_month_old(self, response):
        '''
        Only for issues up to 2015 (included). 
        Afterwards, the naming changes. 

        Args:
            response (str): text fetched from the url (result of GET)

        Returns:
            dict: {year(int): links(list)}, where the links can have 
            one link or two links (one link from 2008, two links before)

        '''
        parsed_page = self.parse_page(response)
        only_links = self.extract_links(parsed_page)
        
        # Two issues for months
        months = [x.split('/')[-1] for x in only_links]
        # Cleaning to focus on the whole month
        months_cleaned = set([m.split('-')[0] for m in months])
        
        wt_by_month_dict = dict()
        for m in months_cleaned:
            issues_in_month = [x for x in only_links if x.split('/')[-1].split('-')[0] == m]
            # From 2008, a single issue for each version-month
            if len(issues_in_month) == 1:
                wt_by_month_dict[m] = issues_in_month[0]
            # Up to 2007, two issues for each month
            else:
                wt_by_month_dict[m] = issues_in_month
    
        return wt_by_month_dict 
    

    def get_public_or_study(self, response):
        '''
        Needed from 2008 (included), year of the 
        introduction of Study and Public editions. It looks 
        for the links to the two different editions. 
     
        Args:
            response (str): text fetched with a GET, from the page of 
            a specific month of WT

        Returns:
            str, str: the two links to the public and study editions
        '''
        parsed_page = self.parse_page(response)
        only_links = self.extract_links(parsed_page)
    
        public = [x for x in only_links if x.split('/')[-1] == 'public-edition'][0]
        study = [x for x in only_links if x.split('/')[-1] == 'study-edition'][0]
    
        return public, study
    

    def get_issues_links(self, response):
        '''
        Retrieves the links for each issue of a single year. 

        Args:
            response (str): text fetched with a GET, from the page of a public 
            or study edition with the name convention valid from 2016

        Returns:
            dict: {issue_id(str): link(str)}, dictionary with a URL for each 
            issue of the input month/edition. The issue_id can be a month 
            followed by 1 or 15, or a string like 'no1', depending on the year.
        '''
        parsed_page = self.parse_page(response)
        only_links = self.extract_links(parsed_page)
    
        wt_by_month_dict = dict(zip([x.split('/')[-1] for x in only_links], only_links))
    
        return wt_by_month_dict 
    

    def get_articles_links_by_title(self, response):
        '''
        Extract from the main page of an issue all the article titles
        and the corresponding links. Handles the multi-lines titles. 
    
        Args:
            response (str): text fetched with a GET from the issue's URL

        Returns:
            dict: {title(str): link(str)}, dictionary with a link for each
            article; the key is the article's title
        '''
    
        parsed_page = self.parse_page(response)
        only_links = self.extract_links(parsed_page)
    
        sections = parsed_page.findAll('a', class_ = re.compile('^jwac'))
    
        # using the BS stripped_strings generator to extract the clean text
        get_title = lambda x: next(x.stripped_strings)
    
        only_titles = []
        for s in sections:
            title_blocks = s.findAll('div', class_ = re.compile('^cardLine'))
            titles = [get_title(block) for block in title_blocks]
            titles_joined = ' - '.join(titles)
    
            only_titles.append(titles_joined)    
    
        articles_by_title = dict(zip(only_titles, only_links))
    
        return articles_by_title
    

    def scrape_page(self, url):
        '''
        Scrapes the page from the url with no
        further processing
        '''
        scraped_page = requests.get(url).text

        return scraped_page  


    def dump_scraped_page(self, scraped_page):
        '''
        Saves the scraped raw page in a document database
        '''
        #TODO
        pass 

 
    def parse_page(self, scraped_page):
        '''
        ''' 
        parsed_page = BeautifulSoup(scraped_page, 'lxml')
    
        return parsed_page 
    

    def extract_links(self, parsed_page):
        '''
        Extract the links from the page, using the convention
        present in the JW website
        '''
        
        subset_with_links = parsed_page.findAll('a', attrs = {'href': re.compile('.*'), 'class': re.compile('^jwac')}) 
        only_links = [self.root + x['href'] for x in subset_with_links]
        
        return only_links


    async def get_page_content(self, url, session):

        response = await session.request(method='GET', url=url)
        
        return await response.text()



# if __name__ == "__main__":

   # url = 'https://wol.jw.org/en/wol/library/r1/lp-e/all-publications/watchtower'
   # root = 'https://wol.jw.org'

    #links =  get_years(url)
    #print(links)

    #links_by_year = get_wt_links_by_month(links[2007])
    #print(links_by_year) 

    #print("")

    #y_2008_pub, y_2008_study = get_public_or_study(links[2008])
    #links_2008_public = get_wt_links_by_month(y_2008_pub)
    #print(links_2008_public)
    #links_2008_study = get_wt_links_by_month(y_2008_study)
    #print(links_2008_study)

    #print("")
    #
    #y_2018_pub, y_2018_study = get_public_or_study(links[2018])
    #links_2018_public = get_wt_links_by_month_post_2015(y_2018_pub)
    #print(links_2018_public)
    #links_2018_study = get_wt_links_by_month_post_2015(y_2018_study)
    #print(links_2018_study)
    #
    #print("")

    #dec_08_articles_by_title = get_articles_links_by_title_v2(links_2008_public['december'])
    #print(dec_08_articles_by_title) 

    #print("")
    #an_article = extract_text_from_article('https://wol.jw.org/en/wol/d/r1/lp-e/2008885')
    #print(an_article) 
