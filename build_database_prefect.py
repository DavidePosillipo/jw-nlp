import prefect
from prefect import task, Flow, Parameter
from prefect.tasks.shell import ShellTask
from datetime import datetime
import json
import psycopg2

from build_wt_json_library import scrape_wt_batch
from jwnlp.utils.config import Config

logger = prefect.context.get("logger")

@task
def create_db(user: str, database: str):
    '''
    Create the database if not yet present.

    Args:
        user (str): the name of the database user
        database (str): the name of the database to be created

    Returns:
        str: the command to be executed by the ShellTask
    '''
    command = f"echo \"SELECT 'CREATE DATABASE {database}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '{database}')\gexec\" | psql -U {user}" 

    return command

@task
def create_db_schema(user: str, database: str):
    '''
    Create the database schema for the new database (only once)

    Args:
        user (str): name of the database user
        database (str): name of the database

    Returns:
        str: the command to be executed by the ShellTask
    '''
    command = f"psql -U {user} -d {database} -f ./db/db_schema.sql" 

    return command

@task
def scrape_batch(language: str, starting_year: int):
    '''
    Scrape the Watchtower articles in the JW website in batch mode, only the first time.

    Args:
        language (str): the language of the articles to be scraped
        starting_year (int): the first year of the collections of articles to be scraped

    Returns:
        None
    '''
    #TODO put language parameters in some config file 
    scrape_wt_batch(language, starting_year)

@task
def populate_database(user: str, database: str):
    '''
    Populate the database with the available files.

    Args:
        user (str): the database username
        database (str): the name of the database to be populated

    Returns
        str: the command to be executed by the ShellTask
    '''
    command = f"sh ./db/populate_db.sh --folder ./data/parsed --user {user} --database {database}"

    return command

shell_task = ShellTask()

with Flow("jw-nlp") as flow:

    username = Config.user_name
    database_name = Config.database_name

    create_db_cmd = create_db(user=username, database=database_name)
    create_db_via_shell = ShellTask(create_db_cmd)

    create_schema_cmd = create_db_schema(user=username,
        database=database_name,
        upstream_tasks=[create_db_via_shell])
    create_schema_via_shell = ShellTask(create_schema_cmd)

    # Check if the batch scraping already happened
    conn = psycopg2.connect(f"dbname={database_name} user={username}")
    cur = conn.cursor()
    cur.execute("""
                SELECT is_batch_downloaded
                FROM publications
                WHERE name='Watchtower';
                """
                )
    # If is_batch_downloaded is False, then perform the batch scraping
    if !cur.fetchall():
        scrape_batch(language='en', 
                     starting_year=2006, #2006 only for debug
                     upstream_tasks=[create_schema_via_shell])
        
        
   
flow.register(project_name="jwnlp") 

    

