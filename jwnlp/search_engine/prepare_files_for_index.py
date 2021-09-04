import json
from argparse import ArgumentParser
import os
import pickle

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("-d", "--directory", dest="directory",
                        help="Root directory with the JSON to be indexed")
    args = parser.parse_args()

    documents = []

    for root, dirs, files in os.walk(args.directory):
        print("Workin on", root)
        for f in files:
            if f.endswith(".json"):
                with open(os.path.join(root, f), "r") as open_file:
                    article = json.load(open_file)

                    # ordering paragraphs by parId
                    paragraphs = {int(k[1:]): v for (k,v) in article['paragraphs'].items()}
                    article['paragraphs'] = '\n'.join([p[1] for p in sorted(paragraphs.items())])

                    documents.append(article)

    with open(os.path.join(args.directory, "array_of_docs_to_index.pkl"), "wb") as out:
        pickle.dump(documents, out) 
 
