import requests
import re
from bs4 import BeautifulSoup

def get_years(url):
    '''
    Access the mainpage and retrieve the links for each single
    year of WT
    '''

    parsed_page = parse_page(url)
 
    only_links = extract_links(parsed_page)
    
    search_years = re.compile(r"(?<=-)[0-9]+")
    years = [int(search_years.search(x).group()) for x in only_links]
    wt_for_years_dict = dict(zip(years, only_links))

    return wt_for_years_dict

def get_months(url):
    '''
    Only for issues up to 2015 (included). 
    Afterwards, the naming changes. 
    '''
    parsed_page = parse_page(url)
    only_links = extract_links(parsed_page)
    
    # Two issues for months
    months = [x.split('/')[-1] for x in only_links]
    # Cleaning to focus on the whole month
    months_cleaned = set([m.split('-')[0] for m in months])
    
    wt_for_months_dict = dict()
    for m in months_cleaned:
        wt_for_months_dict[m] = [x for x in only_links if x.split('/')[-1].split('-')[0] == m]

    return wt_for_months_dict

def get_public_or_study(url):
    '''
    Needed from 2008 (included), year of the 
    introduction of Study and Public editions
    '''
    parsed_page = parse_page(url)
    only_links = extract_links(parsed_page)

    public = [x for x in only_links if x.split('/')[-1] == 'public-edition'][0]
    study = [x for x in only_links if x.split('/')[-1] == 'study-edition'][0]

    return public, study

def parse_page(url):
    
    page = requests.get(url)
    parsed_page = BeautifulSoup(page.text, 'lxml')

    return parsed_page 

def extract_links(parsed_page):
    '''
    Extract the links from the page, using the convention
    present in the JW website
    '''
    
    root = 'https://wol.jw.org'

    subset_with_links = parsed_page.findAll('a', attrs = {'href': re.compile('.*'), 'class': re.compile('^jwac')}) 
    only_links = [root + x['href'] for x in subset_with_links]
    
    return only_links 

if __name__ == "__main__":

    url = 'https://wol.jw.org/en/wol/library/r1/lp-e/all-publications/watchtower'
    root = 'https://wol.jw.org'

    links =  get_years(url)
    #print(links)

    links_a_month = get_months(links[2007])
    print(links_a_month) 

    y_2008_pub, y_2008_study = get_public_or_study(links[2008])
    links_2008_public = get_months(y_2008_pub)
    print(links_2008_public)
    links_2008_study = get_months(y_2008_study)
    print(links_2008_study)
    
