import prefect
from prefect import task, Flow, Parameter
from prefect.engine import signals
from prefect.tasks.shell import ShellTask
from prefect.run_configs import LocalRun
from datetime import datetime
import json
import psycopg2
import logging

from build_wt_json_library import scrape_wt_batch
from jwnlp.utils.config import Config

logger = prefect.context.get("logger")
#logger = logging.getLogger(__name__)

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
def scrape_batch(language: str, starting_year: int, final_year: int, user: str, database: str):
    '''
    Scrape the Watchtower articles in the JW website in batch mode, only the first time.

    Args:
        language (str): the language of the articles to be scraped
        starting_year (int): the first year of the collections of articles to be scraped
        final_year (int): the last year of the collections of articles to be scraped

    Returns:
        prefect Signal: Success or Fail 
    '''
    conn = psycopg2.connect(f"dbname={database} user={user}")
    cur = conn.cursor()
    cur.execute("""
                SELECT is_batch_downloaded
                FROM publications
                WHERE name='Watchtower';
                """
                )
    if cur.fetchall()[0][0]:
        logger.info("Batch scraping already happened, skipping this task")
        raise signals.SKIP()
    else:
        try:
            logger.info("Executing batch scraping. It may take a while...")
            scrape_wt_batch(language, starting_year, final_year)
            logger.info("Batch scraping completed")
            return signals.SUCCESS()
        except:
            logger.info("Batch scraping not successful!")
            return signals.FAIL()    
    
@task
def check_if_batch_exists(user: str, database: str):
    '''
    Check if the database contains already the batch scraping data.
    If not, the flow will perform the batch scraping. 

    Args:
        user (str): the username for the database
        database (str): the name of the database

    Returns:
        boolean: True if the batch exists already
    '''
    conn = psycopg2.connect(f"dbname={database} user={user}")
    cur = conn.cursor()
    cur.execute("""
                SELECT is_batch_downloaded
                FROM publications
                WHERE name='Watchtower';
                """
                )

    return cur.fetchall()[0][0]

@task(log_stdout=True)
def populate_database(user: str, database: str):
    '''
    Populate the database with the available files.

    Args:
        user (str): the database username
        database (str): the name of the database to be populated

    Returns
        str: the command to be executed by the ShellTask
    '''
    print("here")
    #TODO how to pass named arguments?
    command = f"sh ./db/populate_db.sh ./data/parsed {user} {database}"

    return command

shell_task = ShellTask()

with Flow("jw-nlp", run_config=LocalRun()) as flow:

    username = Config.user_name
    database_name = Config.database_name

    create_db_cmd = create_db(user=username, database=database_name)
    create_db_via_shell = shell_task(create_db_cmd)

    #TODO the schema needs to be created only once, when the db is created
    create_schema_cmd = create_db_schema(user=username,
        database=database_name,
        upstream_tasks=[create_db_via_shell])
    create_schema_via_shell = shell_task(create_schema_cmd)

   # need_to_batch_scraping = check_if_batch_exists(user=username, database=database_name,
   #                             upstream_tasks=[create_db_via_shell, create_schema_via_shell])

    scrape_batch_result = scrape_batch(language='en', 
                                    starting_year=2006, #2006 only for debug
                                    final_year=2009, #2009 only for debug
                                    user=username,
                                    database=database_name,
                                    upstream_tasks=[create_schema_via_shell])

    # by default skipped if the upstream task is skipped
    populate_db_cmd = populate_database(user=username, database=database_name,
                                upstream_tasks=[scrape_batch_result])
    populate_db_via_shell = shell_task(populate_db_cmd)
        
        
   
flow.register(project_name="jwnlp") 

    

