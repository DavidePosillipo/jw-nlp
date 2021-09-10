from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import json
import pickle
import os

def summarize_article(article_dict: dict, max_length=150, min_length=0, length_penalty=2.0):
    '''
    Uses the HuggingFace transformers to summarize
    the article given as input 

    Args:
        article_dict (dict): Dictionary with the article data and metadata
        max_length (int): max length of the output (via HuggingFace)
        min_length (int): min length of the output (via HuggingFace)
        length_penalty (float): ???

    Returns:
        str: the summarized article
    '''
    #TODO summary for each paragraph? count of words of entire article to decide?

    paragraphs = {int(k[1:]): v for (k,v) in article_dict['paragraphs'].items()}
    article = [p[1] for p in sorted(paragraphs.items())]

    model = AutoModelForSeq2SeqLM.from_pretrained("t5-base")
    tokenizer = AutoTokenizer.from_pretrained("t5-base")

    summarized_pars = []
    for par in article: 
        inputs = tokenizer("summarize: " + par, return_tensors="pt", max_length=512, truncation=True)
    
        outputs = model.generate(
    	inputs["input_ids"],
    	max_length=max_length,
    	min_length=min_length,
    	length_penalty=length_penalty,
    	num_beams=4,
    	early_stopping=True
    	)

        summarized_pars.append(tokenizer.decode(outputs[0]))
    
    return '\n'.join(summarized_pars) 

