from jwnlp.scraper.wt_scraper_new import wtScraper
import json
import pickle
import aiohttp
import asyncio

if __name__ == '__main__':

    scraper = wtScraper('en')

    links_by_year = scraper.get_years() 
    #links_by_month = {year: scraper.get_links_by_month(link) for (year,link) in links_by_year.items()}

    articles_links_pre_2008 = dict()
    articles_links_post_2008_study = dict()
    articles_links_post_2008_public = dict()

    links_by_year_pre_2008 = {y: l for (y, l) in links_by_year.items() if y<2008}

    async def fetch(url, session):
         async with session.get(url) as response: 
             return await response.text() 


    async def main():
        tasks = []
        async with aiohttp.ClientSession() as session:
            for url in links_by_year_pre_2008.values():
                task = asyncio.ensure_future(fetch(url, session))
                tasks.append(task)

            pages_contents = await asyncio.gather(*tasks)
            issues_links = [scraper.get_wt_links_by_month(page) for page in pages_contents]
            output_dict = dict(zip(links_by_year_pre_2008.keys(), issues_links))
            print(output_dict)

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(main())
    loop.run_until_complete(future)
