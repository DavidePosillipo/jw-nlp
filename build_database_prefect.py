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
def scrape_batch(publication: str, language: str, starting_year: int, final_year: int, user: str, database: str):
    '''
    Scrape the Watchtower articles in the JW website in batch mode, only the first time.

    Args:
        publication (str): the name of the publication to be scraped
        language (str): the language of the articles to be scraped
        starting_year (int): the first year of the collections of articles to be scraped
        final_year (int): the last year of the collections of articles to be scraped

    Returns:
        prefect Signal: Success or Fail 
    '''
    conn = psycopg2.connect(f"dbname={database} user={user}")
    cur = conn.cursor()
    cur.execute(f"""
                SELECT is_batch_downloaded
                FROM publications
                WHERE name='{publication}' AND language='{language}';
                """
                )
    if cur.fetchall()[0][0]:
        logger.info("Batch scraping already happened, skipping this task")
        raise signals.SKIP()
    else:
        try:
            logger.info("Executing batch scraping. It may take a while...")
            #TODO select the proper function for different publications (now it is wt)
            scrape_wt_batch(language, starting_year, final_year)
            logger.info("Batch scraping completed")
            return signals.SUCCESS()
        except:
            logger.info("Batch scraping not successful!")
            return signals.FAIL()    
    
@task(skip_on_upstream_skip=False)
def update_publications_table(user: str, database: str, publication: str, language: str, 
                                schema_created=False,
                                batch_downloaded=False,
                                batch_uploaded_on_db=False):

    if schema_created:
        conn = psycopg2.connect(f"dbname={database} user={user}")
        cur = conn.cursor()
        cur.execute(f"""
                    INSERT INTO publications(name, language, is_periodical, is_batch_downloaded, is_batch_uploaded_on_db, creation_date, last_update)
                        VALUES ('{publication}', '{language}', true, false, false, CURRENT_DATE, CURRENT_DATE)
                        ON CONFLICT (name, language) DO NOTHING;
                    """
                    )
        conn.commit()
        cur.close()
        conn.close()
    elif batch_downloaded:
        conn = psycopg2.connect(f"dbname={database} user={user}")
        cur = conn.cursor()
        cur.execute(f"""
                    UPDATE publications
                    SET
                        is_batch_downloaded = true,
                        last_update = CURRENT_DATE
                    WHERE
                        name = '{publication}'
                        AND
                        language = '{language}'
                    ; 
                    """
                    )
        conn.commit()
        cur.close()
        conn.close()
    elif batch_uploaded_on_db:
        conn = psycopg2.connect(f"dbname={database} user={user}")
        cur = conn.cursor()
        cur.execute(f"""
                    UPDATE publications
                    SET
                        is_batch_uploaded_on_db = true,
                        last_update = CURRENT_DATE
                    WHERE
                        name = '{publication}'
                        AND
                        language = '{language}'
                    ; 
                    """
                    )
        conn.commit()
        cur.close()
        conn.close()
    else:
        raise signals.SKIP()

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
    conn = psycopg2.connect(f"dbname={database} user={user}")
    cur = conn.cursor()
    cur.execute(f"""
                SELECT is_batch_uploaded_on_db 
                FROM publications
                WHERE name='{publication}' AND language='{language}';
                """
                )
    if cur.fetchall()[0][0]:
        logger.info("Batch scraping already happened, skipping this task")
        raise signals.SKIP()
    else:
        try:
        logger.info("Populating the database with the scraped batch")
        #TODO how to pass named arguments?
        command = f"sh ./db/populate_db.sh ./data/parsed {user} {database}"
    return command

shell_task = ShellTask()

with Flow("jw-nlp", run_config=LocalRun()) as flow:

    username = Config.user_name
    database_name = Config.database_name

    publication = "Watchtower"
    language = "en"

    #TODO generalize to creation of other tables for other publications. 
    # -> currently only watchtowers in english are stored
    create_db_cmd = create_db(user=username, database=database_name)
    create_db_via_shell = shell_task(create_db_cmd)

    
    create_schema_cmd = create_db_schema(user=username,
        database=database_name,
        upstream_tasks=[create_db_via_shell])
    create_schema_via_shell = shell_task(create_schema_cmd)
    
    # The schema was created
    up_pub_tab_1 = update_publications_table(user=username,
                                database=database_name,
                                publication=publication,
                                language=language,
                                schema_created=True,
                                upstream_tasks=[create_schema_via_shell])

    scrape_batch_result = scrape_batch(publication=publication,
                                    language=language, 
                                    starting_year=2006, #2006 only for debug
                                    final_year=2009, #2009 only for debug
                                    user=username,
                                    database=database_name,
                                    upstream_tasks=[up_pub_tab_1])

    # The scraped batch was downloaded 
    up_pub_tab_2 = update_publications_table(user=username,
                                database=database_name,
                                publication=publication,
                                language=language,
                                batch_downloaded=True,
                                upstream_tasks=[scrape_batch_result])

    # by default skipped if the upstream task is skipped
    #TODO add parameter for table name and path where the json are stored
    populate_db_cmd = populate_database(user=username, 
                                        database=database_name,
                                upstream_tasks=[up_pub_tab_2])
    populate_db_via_shell = shell_task(populate_db_cmd)
        
    # The scraped batch was downloaded 
    up_pub_tab_3 = update_publications_table(user=username,
                                database=database_name,
                                publication=publication,
                                language=language,
                                batch_uploaded_on_db=True,
                                upstream_tasks=[populate_db_via_shell])

       
flow.register(project_name="jwnlp") 

    

