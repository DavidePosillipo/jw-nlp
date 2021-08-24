from jwnlp.scraper.wt_scraper import wtScraper
import json

if __name__ == '__main__':

    scraper = wtScraper('en')

    links_by_year = scraper.get_years() 
    #links_by_month = {year: scraper.get_links_by_month(link) for (year,link) in links_by_year.items()}

    articles_links_pre_2008 = dict()
    articles_links_post_2008_study = dict()
    articles_links_post_2008_public = dict()

    for year in links_by_year.keys():
        print("Working on year ", year)
        issues_links = dict()
        # for the years from 1950 to 2007
        if year<2008:
            issues_links = scraper.get_wt_links_by_month(links_by_year[year]) 
            for month in issues_links.keys():
                print(month)
                # First issue of the month ("1")
                articles_links_pre_2008[(year, month, "no-1")] = scraper.get_articles_links_by_title(issues_links[month][0])
                # Second issue of the month ("15")
                articles_links_pre_2008[(year, month, "no-15")] = scraper.get_articles_links_by_title(issues_links[month][1])
        else:
            print('todo')
            #TODO

    with open("./temp/links.json", "w") as f:
        json.dump(articles_links_pre_2008, f) 
            
        
        

    # article_parser = articleParser(2000, "aaa", "bbb", pars)
    # article_parser.save_article(db)
