import prefect
from prefect import task, Flow, Parameter
from prefect.tasks.shell import ShellTask
from datetime import datetime
import json

logger = prefect.context.get("logger")

@task
def build_library():
    '''
    Checks if the library exists and 
    if not, it start the batch scraping
    '''
    pass


@task
def update_library():
    '''
    Download the last issues from
    the website
    '''
    pass


@task
def build_index():
    '''
    Build the index for the search engine
    '''
    pass


@task
def update_index():
    '''
    Update the index with the new publications
    '''
    pass


with Flow("jw-nlp") as flow:

    build_library()

    update_library()

    build_index()

    update_index()

