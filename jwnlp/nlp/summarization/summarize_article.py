from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import json
import pickle
import os

def summarize_article(filename: str, article_id: str, max_length=150, min_length=40, length_penalty=2.0):
    '''
    Uses the HuggingFace transformers to summarize
    the article with given article_id

    Args:
        article_id (str): id of the article that must be summarized
        max_length (int): max length of the output (via HuggingFace)
        min_length (int): min length of the output (via HuggingFace)
        length_penalty (float): ???

    Returns:
        str: the summarized article
    '''

    #TODO read the article from the db or index
    # article = get_article(article_id)

    #TODO summary for each paragraph? count of words of entire article to decide?

    #TODO to remove, only for debug 
#    parser = ArgumentParser()
#    parser.add_argument("-f", "--filename", dest="filename",
#     			help="Filename of the file containing the article")
# 
#    with open(parser.filename, "r") as f:
#        article_dict = json.load(f)
#
    with open(filename, "r") as f:
        article_dict = json.load(f)

    paragraphs = {int(k[1:]): v for (k,v) in article_dict['paragraphs'].items()}
    article = '\n'.join([p[1] for p in sorted(paragraphs.items())])

    model = AutoModelForSeq2SeqLM.from_pretrained("t5-base")
    tokenizer = AutoTokenizer.from_pretrained("t5-base")

    inputs = tokenizer("summarize: " + article, return_tensors="pt", max_length=512, truncation=True)

    outputs = model.generate(
	inputs["input_ids"],
	max_length=max_length,
	min_length=min_length,
	length_penalty=length_penalty,
	num_beams=4,
	early_stopping=True
	)

    return tokenizer.decode(outputs[0])

