import json
from bs4 import BeautifulSoup

class wtArticle:
    #TODO inherit from Article class, that inherits from Publication
    '''
    Represents a Watchtower article and provides methods to parse it
    and to save it as JSON in a database.
    '''
    def __init__(self, year: int, title: str, publication: str, edition: str, url: str):
        self.year = year
        self.title = title
        self.publication = publication
        self.paragraphs = paragraphs
        self.url = url 

        self.output_dict = dict()
        self.output_dict['year'] = self.year
        self.output_dict['title'] = self.title
        self.output_dict['publication'] = self.publication

        self.paragraphs = self.extract_pargraphs_from_article(self.url)
 

    def parse(self, scraped_page):
    
        paragraphs = self.extract_paragraphs_from_article(scraped_page)
        
        #TODO if needed, here intermediate pre-processing steps

        self.output_dict['paragraphs'] = paragraphs


    def extract_paragraphs_from_article(self, scraped_page):
        '''
        Extract the text from the paragraphs inside the
        articles page and returns a dictionary as output
        '''
        parsed_page = BeautifulSoup(scraped_page, 'lxml') 
    
        article = parsed_page.find('article')
        paragraphs = article.findAll('p')
    
        article_text = dict() 
        for p in paragraphs:
            p_id = p['id']
            p_iterator = p.stripped_strings
            p_text = []
            for chunk in p_iterator:
                p_text.append(chunk)
            article_text[p_id] = ' '.join(p_text)

        return article_text
 

#    def process_paragraphs(self):
#        '''
#        Manipulates the content of the paragraphs
#        and saves them into the output dictionary
#        '''
#        for p in self.paragraphs:
#            pass
#
#        self.output['paragraphs'] = self.paragraphs
#

    def save_article(self, json_file):
    
        with open(json_file, 'w') as f:
            json.dump(self.output_dict, f)
    

