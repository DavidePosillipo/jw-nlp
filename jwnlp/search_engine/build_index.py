import meilisearch
import json
from argparse import ArgumentParser
import pickle

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("-f", "--filename", dest="filename",
     			help="Filename of the file containing the documents for the index")
    parser.add_argument("-i", "--indexname", dest="indexname",
 			help="Name of the index to create or update")
    parser.add_argument("-k", "--primary_key", dest="primary_key",
			help="Name of the field used as primary key")
    args = parser.parse_args() 

    # Loading the batch of articles to index
    with open(args.filename, "rb") as f:
        documents = pickle.load(f) 

    client = meilisearch.Client('http://127.0.0.1:7700')
    
    client.index(args.indexname).add_documents(documents, primary_key=args.primary_key)


