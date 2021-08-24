from jwnlp.scraper.wt_scraper import wtScraper

if __name__ == '__main__':

    scraper = wtScraper('en')

    links_by_year = scraper.get_years() 

    print(links_by_year)



    # article_parser = articleParser(2000, "aaa", "bbb", pars)
    # article_parser.save_article(db)
