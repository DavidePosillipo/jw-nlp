import json
from bs4 import BeautifulSoup
import os

class ArticleParser:
    '''
    Class for the parsing of WT articles. 
    '''
    def __init__(self, publication: str):
        self.publication = publication

 
    def extract_paragraphs_from_article(self, response):
        '''
        Extract the paragraphs from the article, without further
        preprocessing. 

        Args:
            response (str): text fetched from the URL with a GET

        Returns:
            dict: {paragraph_id(str): paragraph(bs4.element.Tag)},
            dictionary with the paragraphs in form of Beautiful Soup
            element. 
        '''
        parsed_page = BeautifulSoup(response, 'lxml') 
    
        article = parsed_page.find('article')
        paragraphs = article.findAll('p')

        paragraphs_dict = {p['id']: p for p in paragraphs}

        return paragraphs_dict
    
        
    def process_paragraphs(self, bs_paragraphs):
        '''
        Manipulates the content of the paragraphs
        and saves them into the output dictionary

        Args:
            bs_paragraphs (dict): dictionary with the article
            paragraphs in form of bs4.element.Tag (Beautiful Soup).

        Returns:
            dict: dictionary with pre-processed text of the paragraphs
            {paragraph_id(str): paragraph_text(str)}
        '''
        article_text = dict() 
        for p_id, content in bs_paragraphs.items():
            p_iterator = content.stripped_strings
            p_text = []
            for chunk in p_iterator:
                p_text.append(chunk)
            article_text[p_id] = ' '.join(p_text)

        return article_text


    def save_article_to_json(self, output_folder: str, year: int, edition: str, issue_id: str, paragraphs: dict, url: str, language: str, title: str):
        '''
        Creates a JSON object/file that stores all the information
        about the article. 

        Args:
            output_file (str): destionation JSON file
            year (int): year of the article
            edition (str): edition of the wt (Public, Study or Generic)
            issue_id (str): the monthly or bi-monthly id of the article
            paragraphs (dict): the dictionary with the text for each paragraph
            url (str): the URL to the articlei
            language (str): the language of the article
            title (str): the title of the article

        Returns:
            None
        '''

        article_id = url.split('/')[-1]

        article = {
                    "article_id": article_id,
                    "year": year,
                    "edition": edition,
                    "url": url,
                    "language": language,
                    "issue_id": issue_id,
                    "title": title,
                    "paragraphs": paragraphs
                  }

        with open(os.path.join(output_folder, article_id + ".json"), 'w') as f:
            json.dump(article, f)

