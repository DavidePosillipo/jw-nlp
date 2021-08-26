import aiohttp
import asyncio

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


