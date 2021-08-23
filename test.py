from jwnlp.scraper.wt_scraper import wtScraper

if __name__ == '__main__':

    scraper = wtScraper('en')

    links_by_year = scraper.get_years() 

    print(links_by_year)
