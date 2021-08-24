import requests
import re
from bs4 import BeautifulSoup

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
    
        parsed_page = self.parse_page(self.homepage)
     
        only_links = self.extract_links(parsed_page)
        
        search_years = re.compile(r"(?<=-)[0-9]+")
        years = [int(search_years.search(x).group()) for x in only_links]
        wt_for_years_dict = dict(zip(years, only_links))
    
        return wt_for_years_dict
    

    def get_wt_links_by_month(self, url):
        '''
        Only for issues up to 2015 (included). 
        Afterwards, the naming changes. 
        '''
        parsed_page = self.parse_page(url)
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
    

    def get_public_or_study(self, url):
        '''
        Needed from 2008 (included), year of the 
        introduction of Study and Public editions
        '''
        parsed_page = self.parse_page(url)
        only_links = self.extract_links(parsed_page)
    
        public = [x for x in only_links if x.split('/')[-1] == 'public-edition'][0]
        study = [x for x in only_links if x.split('/')[-1] == 'study-edition'][0]
    
        return public, study
    

    def get_wt_links_by_month_post_2015(self, url):
        '''
        Retrieves the links for both study and public version, from 2016.
        This is needed due to the new naming convention
        introduced in 2016. 
        '''
        parsed_page = self.parse_page(url)
        only_links = self.extract_links(parsed_page)
    
        wt_by_month_dict = dict(zip([x.split('/')[-1] for x in only_links], only_links))
    
        return wt_by_month_dict 
    

    def get_articles_links_by_title(self, url):
        '''
        Extract from the main page of an issue all the article titles
        and the corresponding links. Handles the multi-lines titles. 
        '''
    
        parsed_page = self.parse_page(url)
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

 
    def parse_page(self, url):
        '''
        Open the url and use BeautifulSoup to 
        parse the xml tree
        ''' 
        scraped_page = self.scrape_page(url)
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
