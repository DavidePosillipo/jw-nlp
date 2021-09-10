import prefect
from prefect import task, Flow, Parameter
from prefect.tasks.shell import ShellTask
from datetime import datetime
import json

logger = prefect.context.get("logger")

@task
def create_db():
    '''
    Create the database if not yet present. The db name is by default jwnlp
    '''
    command = f"echo \"SELECT 'CREATE DATABASE jwnlp' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'jwnlp')\gexec\" | psql" 

    return command

@task
def create_db_schema():
    '''
    Create the database schema for the new database (only once)
    '''
    #TODO call the sql file via psql with a shellTask
    pass

@task
def scrape_batch():
    '''
    Scrape the JW website in batch mode, only the first time.
    '''
    #TODO plug in the scraping big script. Call as function?
    pass 

@task
def populate_database():
    '''
    Populate the database with the available files.
    '''
    #TODO call the shell script already written
    pass


shell_task = ShellTask()

with Flow("jw-nlp") as flow:

    create_db_cmd = create_db()
    create_db_via_shell = ShellTask(create_db_cmd)

