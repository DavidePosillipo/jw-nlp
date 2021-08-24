class articleParser:

    def __init__(self, year: int, title: str, publication: str, paragraphs: dict):
        self.year = year
        self.title = title
        self.publication = publication
        self.paragraphs = paragraphs

        self.output_dict = dict()
        self.output_dict['year'] = self.year
        self.output_dict['title'] = self.title
        self.output_dict['publication'] = self.publication

        process_paragraphs()

    def process_paragraphs(self):

        for p in self.paragraphs:
            pass

        self.output['paragraphs'] = self.paragraphs

    def save_article(self, json_file):
    
        with open(json_file, 'w') as f:
            json.dump(self.output_dict, f)
   
    def write_paragraphs_to_json(self, paragraphs, json_file):
        '''
        Takes the paragraphs input (dictionary) and 
        '''
        with open(json_file, 'w') as f:
            for p in paragraphs:
                
         
